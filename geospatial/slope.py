import math

# radius of Earth (in meters)
R = 6371000

class MatchedPoint():
    lon = None
    lat = None
    alt = None
    distFromRef = None
    def __init__(self, lon, lat, alt, distFromRef):
        self.lon = float(lon)
        self.lat = float(lat)
        self.alt = float(alt)
        self.distFromRef = float(distFromRef)
    def calSlope(self, probe):
        dist = self.calDist(probe)
        if dist == 0:
            return None
        return math.atan((probe.alt - self.alt)/dist) * 180 / math.pi
    def calDist(self, probe):

        dlon = self.lon - probe.lon
        dlat = self.lat - probe.lat
        a = math.sin(dlat/2)**2 + math.cos(probe.lat) * math.cos(self.lat) * math.sin(dlon/2)**2
        c = 2 * math.atan2(a**0.5, (1-a)**0.5)
        d = R * c
        return d

class Slope():
    slope = None
    distFromRef = None
    def __init__(self, slope, distFromRef):
        self.slope = slope
        self.distFromRef = distFromRef


lines = open("mapped.txt").readlines()
sets = {}
for line in lines:
    cols = line[:-1].split(",")
    lat = cols[3]
    lon = cols[4]
    alt = cols[5].strip()
    linkid = cols[8].strip()
    if alt == None or alt == "":
        continue
    distFromRef = cols[-1].strip()
    if linkid not in sets:
        sets[linkid] = []
    sets[linkid].append(MatchedPoint(lon, lat, alt, distFromRef))

# For each link, calculate all its slopes with probes on it
slopes = {}
for linkid in sets:
    probes = sets[linkid]
    probes.sort(key=lambda x: x.distFromRef)
    for i in range(1, len(probes)):
        slope = probes[i-1].calSlope(probes[i])
        if slope == None:
            continue
        if linkid not in slopes:
            slopes[linkid] = []
        slopes[linkid].append(Slope(slope, probes[i].distFromRef))


lines = open("Partition6467LinkData.csv").readlines()
error = 0.0
count = 0
badError = 5
badCount = 0
nearDist = 8
maxError = 0
for line in lines:
    cols = line[:-1].split(',')
    slopeinfoCol = cols[-1].strip()
    if slopeinfoCol == "":
        continue
    linkid = cols[0]
    if linkid not in slopes:
        continue
    slopeinfos = slopeinfoCol.split('|')
    for test_slopeinfo in slopeinfos:
        test_slopeinfo = test_slopeinfo.split('/')
        test_distFromRef = float(test_slopeinfo[0])
        test_slope = float(test_slopeinfo[1])

        cndSlopesSum = 0
        cndCount = 0
        for train_slope in slopes[linkid]:
            if abs(train_slope.distFromRef - test_distFromRef) < nearDist:

                if abs(train_slope.slope) > 30:
                    continue
                cndSlopesSum += train_slope.slope
                cndCount += 1
        if cndCount == 0:
            continue
        approxSlope = cndSlopesSum/cndCount

        maxError = max(maxError, abs(approxSlope - test_slope))
        error += abs(approxSlope - test_slope)
        count += 1


        if abs(approxSlope - test_slope) > badError:

            badCount += 1

print 'average error: ', error/count, '(in decimal degrees)'
print 'bad error count: ', badCount, ' total error count: ', count
print 'max slope error: ', maxError