import tester
import os, time
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

inp = input(f"Please choose one of the following tests [ 1, 2, 3, 4, 5, 6, 7, all ]:")

if inp == 'all':
    result = ""
    for i, test_case in enumerate(tester.TEST_CASES):
        i+=1
        if i!=0:
            time.sleep(1)
        if tester.run_test(*test_case, verbose=True,print_output=True):
            print(f'Test {i}: PASSED')
            result += f'Test {i}: PASSED\n'
        else:
            print(f'Test {i}: FAILED')
            result += f'Test {i}: FAILED\n'
    print("=====SUMMARY:=====")
    print(result)
elif inp.isdigit():
    i = int(inp) - 1 
    if tester.run_test(*tester.TEST_CASES[i], verbose=True,print_output=True):
        print(f'Test {i}: PASSED')
    else:
        print(f'Test {i}: FAILED')
elif inp.startswith('submit'): # grading mode
    i = int(inp.split()[1])-1
    if tester.run_test(*tester.TEST_CASES[i], verbose=False,print_output=False):
        print('PASSED')
    else:
        print('FAILED')
