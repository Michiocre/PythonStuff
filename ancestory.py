import sys
import random

if len(sys.argv) > 1:
    startPop = sys.argv[1]
else:
    startPop = 100000

popGrowth = 0
generationsNum = 20

currentPop = startPop

generations = []

found = False

for i in range(generationsNum):
    if i < generationsNum:
        generations.append([])
        nextPop = int(currentPop - (popGrowth*currentPop));
        if nextPop <= 2:
            generationsNum = i
            break
        for j in range(currentPop):
            person = {'parents': [], 'decendents': set()}
            person['parents'].append(random.randint(0, nextPop-1))

            while True:
                parent = random.randint(0, nextPop-1)
                if person['parents'][0] != parent:
                    person['parents'].append(parent)
                    break

            generations[i].append(person)
        currentPop = nextPop
    if i > 0:
        i2 = i-1
        for j in range(len(generations[i2])):
            if i2 == 0:
                generations[i2][j]['decendents'].add(j)
                #generations[i][j]['decendents'].append(j)
            for parent in generations[i2][j]['parents']:
                for decendent in generations[i2][j]['decendents']:
                    generations[i2+1][parent]['decendents'].add(decendent)
                    # if decendent in generations[i+1][parent]['decendents']:
                    #     pass
                    # else:
                    #     generations[i+1][parent]['decendents'].append(decendent)
                if len(generations[i2+1][parent]['decendents']) == startPop and found == False:
                    print('Gen', i, ' done | First common ancestor if you go back ',i2+1,' Generations')
                    found = True
                    break
            if found:
                break
            generations[i2][j] = None
        if found:
            break
        generations[i2] = None
    print('Gen', i, ' done')
if found == False:
    print('No common ancesters found after ',generationsNum -1,' Generations')

# for i in range(generationsNum):
#     print('[Population Gen', i,']: ',len(generations[i]))
#     for j in range(len(generations[i])):
#         if len(generations[i][j]['decendents']) == startPop:
#             print('[Gen',i,'| Person',j,'| Parents]: ',generations[i][j]['parents'],' [decendents]: E')
#         elif len(generations[i][j]['decendents']) == 0:
#             print('[Gen',i,'| Person',j,'| Parents]: ',generations[i][j]['parents'],' [decendents]: N')
#         else:
#             print('[Gen',i,'| Person',j,'| Parents]: ',generations[i][j]['parents'],' [decendents]: ', generations[i][j]['decendents'])
