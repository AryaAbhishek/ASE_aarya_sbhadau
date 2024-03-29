import re
import operator
# code provided by instructor start with some self modification
def compiler(x):
    "return something that can compile strings of type x"
    try: int(x); return  int
    except:
        try: float(x); return  float
        except ValueError: return str


def string(s):
    "read lines from a string"
    for line in s.splitlines(): yield line


def file(fname):
    "read lines from a fie"
    with open(fname) as fs:
        for line in fs: yield line


def zipped(archive, fname):
    "read lines from a zipped file"
    with zipfile.ZipFile(archive) as z:
        with z.open(fname) as f:
            for line in f: yield line


def rows(src, sep=",", doomed=r'([\n\t\r ]|#.*)'):
    "convert lines into lists, killing whitespace and comments"
    for line in src:
        line = line.strip()
        line = re.sub(doomed, '', line)
        if line:
            yield line.split(sep)


def cells(src, col_len):
    "convert strings into their right types"
    oks = None
    for n, cells in enumerate(src):
        if len(cells) != col_len:
            yield "E> skipping line"
        else:
            oks = [compiler(cell) for cell in cells]
            yield [f(cell) for f,cell in zip(oks,cells)]



def fromString(s):
    "putting it all together"
    tmp = rows(string(s))
    col_name = next(tmp)
    columns = [i for i in range(len(col_name)) if '?' not in col_name[i]]
    yield(operator.itemgetter(*columns)(col_name))
    for lst in cells(tmp, len(col_name)):
        if type(lst) != list:
            yield lst
        else:
            yield list(operator.itemgetter(*columns)(lst))
# code provided by instructor end after some self modification


class Col:
    # initialize n - total numbers used to find mean and SD
    def __init__(self, col_name, pos):
        self.n = 0
        self.col_name = pos
        self.pos = col_name


class Row:
    def __init__(self, cells=[], cooked=[], dom=0):
        self.cells = cells
        self.cooked = cooked
        self.dom = dom


class Num(Col):
    # lo - lowest number, hi - highest number, mu - mean, m2 - summation of square of differences from mean
    def __init__(self, col_name, pos):
        super().__init__(col_name, pos)
        self.mu = self.m2 = self.sd = 0
        self.lo = 10**32
        self.hi = -1*self.lo
        self.col = []

    def add(self, a):  # get the new number and update mu, sd, lo, hi, m2
        self.col.append(a)
        self.n += 1
        if self.lo > a:
            self.lo = a
        if self.hi < a:
            self.hi = a
        d = a - self.mu
        self.mu += d/self.n
        self.m2 += d*(a-self.mu)
        self.sd = self.num_sd()
        return a

    def num_sd(self):  # return Standard Deviation of numbers
        if self.m2 < 0:
            return 0
        if self.n < 2:
            return 0
        return self.m2/(self.n-1)**0.5

    def num_mean(self):  # returns mean of numbers
        return self.mu

    def num_norm(self, c):  # not used in this assignment
        return (c-self.lo)/(self.hi-self.lo + 10**-32)

    def num_less(self, b):  # get new number and update the mu, m2 and sd by removing value the was added by the number
        if self.n < 2:
            self.sd = 0
            return b
        self.n -= 1
        d = b - self.mu
        self.mu -= d / self.n
        self.m2 -= d * (b - self.mu)
        self.sd = self.num_sd()
        return b


class Table:
    def __init__(self):
        self.oid = 1
        self.rows = []
        self.cols = []

    def read(self, lines):
        tbl = fromString(lines)
        for i, row in enumerate(tbl):
            if i == 0:
                for i in range(len(row)):
                    self.cols.append([Num(i, row[i]), self.oid])
                    self.oid += 1
            else:
                if "E> skipping line" not in row:
                    for i in range(len(self.cols)):
                        self.cols[i][0].add(row[i])
                self.rows.append([Row(row), self.oid])
                self.oid += 1

    def dump(self):
        """ while reading file without putting extra checks """
        # file = open("output1.txt", 'w+')
        # temp = []
        # for col in self.cols:
        #     temp.append(col[0].col_name)
        # file.write(str(temp))
        # for row in self.rows:
        #     # print(row[0].cells)
        #     file.write('\n')
        #     file.write(str(row[0].cells))
        # file.close()
        """ While reading file after extra checks """
        # file = open("output2.txt", 'w+')
        # temp = []
        # for col in self.cols:
        #     temp.append(col[0].col_name)
        # file.write(str(temp))
        # for row in self.rows:
        #     # print(row[0].cells)
        #     file.write('\n')
        #     file.write(str(row[0].cells))
        # file.close()

        """While writing in the required format"""
        file = open("output3.txt", "w+")
        file.write("table_columns")
        for i in range(len(self.cols)):
            file.write("\n|\t"+str(i+1))
            file.write("\n|\t|\tn: "+str(self.cols[i][0].n))
            file.write("\n|\t|\tcol_names: "+self.cols[i][0].col_name)
            file.write("\n|\t|\tpos: "+str(self.cols[i][0].pos))
            file.write("\n|\t|\thi: "+str(self.cols[i][0].hi))
            file.write("\n|\t|\tlo: "+str(self.cols[i][0].lo))
            file.write("\n|\t|\tmu: "+str(self.cols[i][0].mu))
            file.write("\n|\t|\tm2: "+str(self.cols[i][0].m2))
            file.write("\n|\t|\tsd: "+str(self.cols[i][0].sd))
            file.write("\nt.oid: "+str(self.cols[i][1]))
        file.write('\ntable_rows')
        for i in range(len(self.rows)):
            file.write("\n|\t" + str(i + 1))
            file.write("\n|\t|\t" + "cells")
            for j in range(len(self.rows[i][0].cells)):
                file.write("\n|\t|\t|\t" + str(j+1)+": "+str(self.rows[i][0].cells[j]))
            file.write("\n|\t|\tcooked: "+ str(self.rows[i][0].cooked))
            file.write("\n|\t|\tdom: "+str(self.rows[i][0].dom))
            file.write("\n|\t|\toid: "+str(self.rows[i][1]))
        file.close()


if __name__ == "__main__":
    # s = """
    # $cloudCover, $temp, $humid, $wind,  $playHours
    # 100,        68,    80,    0,    3   # comments
    # 0,          85,    85,    0,    0
    # 0,          80,    90,    10,   0
    # 60,         83,    86,    0,    4
    # 100,        70,    96,    0,    3
    # 100,        65,    70,    20,   0
    # 70,         64,    65,    15,   5
    # 0,          72,    95,    0,    0
    # 0,          69,    70,    0,    4
    # 80,          75,    80,    0,    3
    # 0,          75,    70,    18,   4
    # 60,         72,    90,    10,   4
    # 40,         81,    75,    0,    2
    # 100,        71,    91,    15,   0
    # """
    # tbl = Table()
    # tbl.read(s)
    # tbl.dump()
    s = """
    $cloudCover, $temp, ?$humid, <wind,  $playHours
      100,        68,    80,    0,    3   # comments
      0,          85,    85,    0,    0

      0,          80,    90,    10,   0
      60,         83,    86,    0,    4
      100,        70,    96,    0,    3
      100,        65,    70,    20,   0
      70,         64,    65,    15,   5
      0,          72,    95,    0,    0
      0,          69,    70,    0,    4
      0,          75,    80,    0,    0
      0,          75,    70,    18,   4
      60,         72,
      40,         81,    75,    0,    2
      100,        71,    91,    15,   0
    """
    tbl = Table()
    tbl.read(s)
    tbl.dump()
