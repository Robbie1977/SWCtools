import os
import sys

minRadius = 1
synapseType = 6
synapseRadius = 1

class Circuit:
    def __init__(self, pointID, type, X, Y, Z, radius, parent):
        self.pointID = pointID
        self.type = type
        self.X = str(float(X) / 100.0)
        self.Y = str(float(Y) / 100.0)
        self.Z = str(float(Z) / 100.0)
        self.parent = str(parent).strip(' \t\n\r')
        if (int(radius)/100.0) < int(minRadius):
            self.radius = str(minRadius)
        else:
            self.radius = str(int(radius)/100.0)
        self.index = -1

    def __repr__(self):
        return repr((self.pointID, self.type, self.X, self.Y, self.Z, self.radius, self.parent))

    def setindex(self, index):
        self.index = index

    def getindex(self):
        return self.index

    def ispoint(self, pointid):
        return str(pointid).strip(' \t\n\r') == str(self.pointID).strip(' \t\n\r')


class Connection:
    def __init__(self, parent, pointID, prepost, X, Y, Z):
        self.pointID = pointID
        self.prepost = prepost
        self.X = str(float(X) / 100.0)
        self.Y = str(float(Y) / 100.0)
        self.Z = str(float(str(Z).strip(' \t\n\r')) / 100.0)
        self.parent = parent
        self.type = "6"
        self.radius = minRadius

    def __repr__(self):
        return repr((self.pointID, self.type, self.X, self.Y, self.Z, self.radius, self.parent))


if __name__ == "__main__":

    if (len(sys.argv) < 3):
        print 'Error: missing arguments!'
        print 'e.g. python compileSWC.py circuit.swc connections.csv outfile.swc'
    else:
        fnameCir = str(sys.argv[1])
        outputList = []
        pointList = []
        conList = []
        if os.path.isfile(fnameCir):
            print 'Loading neuron tracing (circuit): %s...' % fnameCir
            with open(fnameCir) as f:
                content = f.readlines()
            for line in content:
                if line.startswith("#"):
                    outputList.append(line.strip('\n\r'))
                else:
                    item = line.strip('\n\r').split(' ')
                    pointList.append(Circuit(item[0],item[1],item[2],item[3],item[4],item[5],item[6]))
            conZero = list(outputList)
            conOne = list(outputList)
            fnameCon = str(sys.argv[2])
            if os.path.isfile(fnameCon):
                print 'Loading neuron synapses (connections): %s...' % fnameCon
                with open(fnameCon) as f:
                    content = f.readlines()
                for line in content:
                    if "x" in line:
                        print line
                    else:
                        item = line.strip(' \t\n\r').split(',')
                        conList.append(Connection(item[0], item[1], item[2], item[3], item[4], item[5]))
                print 'Sorting data...'
                sorted(pointList, key=lambda circuit: circuit.pointID)
                sorted(conList, key=lambda connection: connection.pointID)
                cirCount = 0
                print 'Re-indexing data...'
                for point in pointList:
                    cirCount += 1
                    point.setindex(cirCount)
                print 'Adding circuit data...'
                for point in pointList:
                    row = []
                    row.append(str(point.getindex()))
                    # used given type unless soma
                    if int(point.parent) > -1:
                        row.append(str(point.type))
                    else:
                        row.append("1")
                    row.append(str(point.X))
                    row.append(str(point.Y))
                    row.append(str(point.Z))
                    row.append(str(point.radius))
                    if int(point.parent) > 0:
                        for p in pointList:
                            if p.ispoint(point.parent):
                                row.append(str(p.getindex()))
                                break
                    else:
                        row.append(str(point.parent))
                    outputList.append(" ".join(row))
                fnameOut = str(sys.argv[3])
                print 'Saving data to %s' % fnameOut
                with file(fnameOut, 'w') as f:
                    for item in outputList:
                        f.write("%s\r\n" % item)
                print 'Creating synapse points...'
                countZero = 0
                countOne = 0
                for con in conList:
                    row = []
                    r = []
                    if con.prepost == "0":
                        countZero += 1
                        row.append(str(countZero))
                    else:
                        countOne += 1
                        row.append(str(countOne))
                    row.append(str(synapseType))
                    row.append(str(con.X))
                    row.append(str(con.Y))
                    row.append(str(con.Z))
                    row.append(str(synapseRadius))
                    for p in pointList:
                        if p.ispoint(con.parent):
                            if con.prepost == "0":
                                countZero += 1
                                row.append(str(countZero))
                                r.append(str(countZero))
                            else:
                                countOne += 1
                                row.append(str(countOne))
                                r.append(str(countOne))
                            r.append("5")
                            r.append(str(p.X))
                            r.append(str(p.Y))
                            r.append(str(p.Z))
                            r.append(str(synapseRadius))
                            r.append("-1")
                            break
                    if con.prepost == "0":
                        conZero.append(" ".join(row))
                        conZero.append(" ".join(r))
                    else:
                        conOne.append(" ".join(row))
                        conOne.append(" ".join(r))
                fnameOutZero = fnameOut.replace('.swc', '_S0.swc')
                print 'Saving data to %s' % fnameOutZero
                with file(fnameOutZero, 'w') as f:
                    for item in conZero:
                        f.write("%s\r\n" % item)
                fnameOutOne = fnameOut.replace('.swc', '_S1.swc')
                print 'Saving data to %s' % fnameOutOne
                with file(fnameOutOne, 'w') as f:
                    for item in conOne:
                        f.write("%s\r\n" % item)
                print 'Done.'
            else:
                print 'File Missing: %s !!!' % (fnameCon)
        else:
            print 'File Missing: %s !!!' % (fnameCir)
