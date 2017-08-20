import random, shelve
'''
Level Build: 0.0
Levels are 44c by 24r space. 1056 blocks.
2 rows are done (ceiling, floor). 968 blocks.
Left/right walls are done for other 22 rows. 924 potential blocks for platforms/enemies/other things.
1) Platforms, perhaps place one central platform block, then 1, 2, or 3 blocks on either side of it...
2) The end platform blocks have 1, 2 blocks underneath for wall-grabbing.
3) A 3 block platform (1+2) with 1 block under both ends would be a 6-block structure on the board.
4) A 7 block platform (1+3) with 2 blocks under both would be a 21-block structure.
'''

level = []
LEVEL_HEIGHT = 24
LEVEL_WIDTH = 44
#level = [[" " for w in range(0,44)] for h in range(0,24)]

def D6_roll():
    D6 = random.randint(1,6)
    return D6

def make_3p(row, j):
    row[j]="P"
    row[j+1]="P"
    row[j-1]="P"

def make_5p(row,j):
    row[j]="P"
    row[j-2]="P"
    row[j-1]="P"
    row[j+1]="P"
    row[j+2]="P"
    
def add_block(row,j):
    row[j]="P"

    
#Create ceiling...with random Exit
ceiling = list("W"*LEVEL_WIDTH)
rando = random.randint(5,30)
ceiling[rando]="X"
print(ceiling)
ceilingJoin = "".join(ceiling) #convert list to a string
level.append(ceilingJoin) #and append to level list

#Create world in loop
for i in range(1,LEVEL_HEIGHT,1):
    row = list("W")+list(" "*42)+list("W") #create row template, air
        
    for j in range(1,2,1): #create random enemies
        if D6_roll() > 4:
            rando_e = random.randint(20, 35)
            row[rando_e]="E"
    
    for j in range(1, LEVEL_WIDTH-1,1): #create 3 or 5 plat below exit
        if level[i-2][j]=="X" and D6_roll()>1:
            make_3p(row,j)
        if level[i-2][j]=="X" and D6_roll()>=4:
            make_5p(row,j)
    
    for j in range(1,LEVEL_WIDTH-1,1): #row below ceiling is air
        if level[i-1][j] == "W" or level[i-1][j] =="X":
            row[j] = " "
    
    for j in range(1, LEVEL_WIDTH-1, 1): #place Ps at max distance
        if i < 5:
            continue
        if level[i-5][j] == "P":
            row[j+7] = "P"
            row[j-7] = "P"
    
    '''for j in range(1, LEVEL_WIDTH-1,1): #place columns, overhangs
        if level[i-1][j]=="P" and D6_roll() >= 5:
            add_block(row,j)'''

    print(row)
    
    #convert work row to string
    rowJoin = "".join(row)
    #append to level list.
    level.append(rowJoin)
    
#Create floor...
floor = list("W"*44)
floorJoin = "".join(floor)
level.append(floorJoin)
print(floor)

#Output to a file
'''shelfFile = shelve.open('level_data')
shelfFile['level'] = level
shelfFile.close()'''

#Validation Stuff
'''print("\nCompressed Level:")        
print(level)
if level[0][0] == level[0+4][0]:
    print("True")
print(len(level[1]))'''