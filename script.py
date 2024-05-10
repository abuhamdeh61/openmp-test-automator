import os
import subprocess
from matplotlib import pyplot as plt # be sure to have matplotlib installed: pip install matplotlib
import pandas as pd # be sure to have pandas installed: pip install pandas

output_path = os.path.join(os.getcwd(), 'output.txt') 
parallel_code_path = os.path.join(os.getcwd(), 'parallel.cpp')
sequential_code_path = os.path.join(os.getcwd(), 'sequential.cpp')

def compileCode(flag = None, code_path = parallel_code_path):
    params = ['g++', code_path, '-std=c++17','-o', 'main.exe']
    if flag:
        params.append(flag)
    subprocess.call(params)
    
def runCode(schedule = None, chunk = None, threads = None):
    #use env variables to set schedule, chunk and threads
    if schedule and chunk:
        os.environ['OMP_SCHEDULE'] = schedule + ',' + str(chunk)
    if threads:
        os.environ['OMP_NUM_THREADS'] = str(threads)
    
    subprocess.call('./main.exe', stdout=open(output_path, 'w'))

def getOutput():
    #get only first line and remove \n
    with open(output_path, 'r') as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        return float(content[0])


def createExperimentsTable(experiments):
    df = pd.DataFrame(experiments, columns=['schedule', 'chunk', 'threads', 'execution_time'])
    print(df)
    df.to_csv('experiments.csv', index=False)

def createBestTable(experiments):
    if experiments:
        parallel_row = min(experiments, key=lambda x: x[3])
        sequential_row = [x for x in experiments if x[0] == 'sequential'][0]
        
        df = pd.DataFrame([parallel_row, sequential_row], columns=['schedule', 'chunk', 'threads', 'execution_time'])
        print(df)
        df.to_csv('best.csv', index=False)

def plotTop10(experiments_df, best_df, sequential_time):
    #check for sequntial is not in top 10    
    #exclude sequential from top 10
    top_experiments_df = experiments_df[experiments_df['schedule'] != 'sequential'].sort_values('execution_time').head(10)
    

    # Get the sequential execution time
    sequential_time = best_df[best_df['schedule'] == 'sequential']['execution_time'].values

    # Plot the data
    plt.figure(figsize=(14, 6))

    # Plot top 10 experiments
    for index, row in top_experiments_df.iterrows():
        plt.bar(str(row['schedule']) + '\nchunk=' + str(int(row['chunk'])) + '\n  threads=' + str(int(row['threads'])) +'\n '+str(row['execution_time'])+'s', row['execution_time'], color='g')

    # Plot sequential execution time
    plt.bar('sequential \n' +str(sequential_time[0])+'s', sequential_time, color='r')

    plt.xlabel('Experiment')
    plt.ylabel('Execution time (s)')
    plt.title('Top 10 fastest experiments and sequential execution time \n green - parallel, red - sequential')
    plt.ylim(0, 3) 
    plt.tight_layout()
    plt.savefig('plot1.png')
    plt.show()
    
def plotFinal(experiments_df, sequential_time):
    mnParallel = experiments_df[experiments_df['schedule'] != 'sequential'].sort_values('execution_time').head(1)
    
    speedup = sequential_time / mnParallel['execution_time'].values[0]
    
    efficiency = speedup / mnParallel['threads'].values[0]

    speedup = float("{:.4f}".format(speedup))
    efficiency = float("{:.4f}".format(efficiency))
    # Create a DataFrame for the table
    data = {'Schedule': [mnParallel['schedule'].values[0], 'Sequential'],
        'Chunk': [int(mnParallel['chunk'].values[0]), 'N/A'],
        'Threads': [int(mnParallel['threads'].values[0]), 'N/A'],
        'Execution Time (s)': [mnParallel['execution_time'].values[0], sequential_time],
        'Speedup': [speedup, 'N/A'],
        'Efficiency': [efficiency, 'N/A']}
    
    df = pd.DataFrame(data)
    
    # Display the table with modified font
    plt.figure(figsize=(10, 6))
    table = plt.table(cellText=df.values, colLabels=df.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    # Add title to table
    plt.title('Experiment Results')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('plot2.png')
    plt.show()

def plot():
    experiments_df = pd.read_csv('experiments.csv')
    best_df = pd.read_csv('best.csv')
    sequential_time =best_df[best_df['schedule'] == 'sequential']['execution_time'].values[0]
    plotTop10(experiments_df, best_df, sequential_time)
    plotFinal(experiments_df, sequential_time)
    

def makeExperiments():
    schedule = ['static', 'dynamic']
    chunk = [1, 2, 4]
    threads = [1, 2, 3, 4]
    experiments = []
    
    total_experiments = len(schedule) * len(chunk) * len(threads)
    compileCode('-fopenmp')
    for s in schedule:
        for c in chunk:
            for t in threads:
                print('Running experiment: ' + str(len(experiments)+1) + '/' + str(total_experiments))
                runCode(s, c, t)
                experiments.append([s, c, t, getOutput()])
                
    #sequential
    compileCode(None,sequential_code_path)
    runCode()
    experiments.append(['sequential', None, None, getOutput()])
    return experiments

def createAnotherExperiments():
    experiments = makeExperiments()
    createExperimentsTable(experiments)
    createBestTable(experiments)


createAnotherExperiments()
plot()

