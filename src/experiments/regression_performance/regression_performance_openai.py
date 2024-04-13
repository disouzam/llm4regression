"""
OpenAI

python -m src.experiments.regression_performance.regression_performance_openai
"""
from src.regressors.llm_regressor import *
from src.dataset_utils import get_dataset
from src.score_utils import scores
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
import tqdm
import json
import os
from pathlib import Path

if 'OPENAI_API_KEY' not in os.environ:
    print("No OpenAI API key found in environment variables. Will attempt to read from `api.key`.")
    if os.path.exists('api.key'):
        with open('api.key') as fin:
            os.environ['OPENAI_API_KEY'] = fin.readlines()[0].strip()
    else:
        print("No `api.key` file found. Please create one with your OpenAI API key or set the `OPENAI_API_KEY` variable.")
        exit()
    
# llm = ChatOpenAI(model_name="gpt-4-turbo-2024-04-09", temperature=0)
# model_name = 'gpt4-turbo-20240409'
llm = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0)
model_name = 'gpt4-turbo'    
# llm = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0)
# model_name = 'chatgpt'
# llm = OpenAI(model_name="davinci-002", temperature=0)
# model_name = 'davinci002'
# llm = OpenAI(model_name="babbage-002", temperature=0)
# model_name = 'babbage002'
with get_openai_callback() as cb:
    for dataset in [
        'regression_ni11',
        'regression_ni22',
        'regression_ni33',
        'regression_ni12',
        'regression_ni13',
        'regression_ni23',

        'original1',
        'original2',
        'original3',
        'original4',
        'original5',
        'friedman1',
        'friedman2',
        'friedman3',

        'simple_random_nn1',
        'transformer1',

        'character_regression1',
        
    ]:
        print(dataset)
        outputs = []
        for seed in tqdm.tqdm(range(1, 101)):
            ((x_train, x_test, y_train, y_test), y_fn) = get_dataset(dataset)(max_train=50, max_test=1, noise=0, random_state=seed, round=True, round_value=2)
            def run():
                # fspt = construct_few_shot_prompt(x_train, y_train, x_test, encoding_type='vanilla')
                # fspt.format(**x_train[i:(i+1)].to_dict('records')[0])
                # fspt = construct_few_shot_prompt(x_train, y_train, x_test, encoding_type='vanilla')
                # print(fspt.format(**x_test.to_dict('records')[0]))
                # print(y_test)
                # exit()
                try:
                    o = llm_regression(llm, x_train, x_test, y_train, y_test, encoding_type='vanilla', add_instr_prefix=True)
                    outputs.append(
                        {
                            **scores(**o), 
                            'full_outputs': o['full_outputs'],
                            'seed'   : seed,
                            'dataset': dataset,
                            'x_train': x_train.to_dict('records'),
                            'x_test' : x_test.to_dict('records'),
                            'y_train': y_train.to_list(),
                            'y_test' : y_test.to_list(),
                        }
                    )
                except KeyboardInterrupt:
                    exit()
                except Exception as e:
                    print('-'*10)
                    print(e)
                    print(dataset, seed)
                    print('-'*10)
                    # print(f"Reached maximum context at {i}.")
                    return
                
            run()
        print(cb)

        Path(f"results/regression_performance/{model_name}/").mkdir(parents=True, exist_ok=True)
        with open(f'results/regression_performance/{model_name}/{dataset}.jsonl', 'w+') as fout:
            for line in outputs:
                _ = fout.write(json.dumps(line))
                _ = fout.write('\n')
