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
        nextPop = int(currentPop - (popGrowth*currentPop))
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
            for parent in generations[i2][j]['parents']:
                for decendent in generations[i2][j]['decendents']:
                    generations[i2+1][parent]['decendents'].add(decendent)
                if len(generations[i2+1][parent]['decendents']) == startPop and found == False:
                    print(
                        'Gen', i, ' done | First common ancestor if you go back ', i2+1, ' Generations')
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
    print('No common ancesters found after ',
          generationsNum - 1, ' Generations')
