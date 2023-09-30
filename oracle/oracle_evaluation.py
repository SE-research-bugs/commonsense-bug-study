
import os
import datetime
import pandas as pd
from colorama import Fore
from sklearn.model_selection import KFold
from sklearn.metrics import f1_score, precision_score, recall_score

from autogluon.multimodal import MultiModalPredictor


# --- configurations ---
dataset_path = './error_messages_dataset.csv'
NUM_FOLDS = 10
current_fold = -1
training_args={
    "model.hf_text.checkpoint_name": "microsoft/deberta-v3-base",

    "optimization.max_epochs": 10,
    "optimization.patience": 3,
    "optimization.val_check_interval": 0.5,
    "optimization.learning_rate": 0.5e-4,
    "optimization.top_k": 3,
    # "optimization.top_k_average_method": "best",

    "env.batch_size": 16,
    "env.per_gpu_batch_size": 16,
}


def load_dataset(path) -> pd.DataFrame:
    all_data = pd.read_csv(path)
    all_data = all_data.sample(frac=1).reset_index(drop=True)
    return all_data


def train(samples_train):
    time_str = datetime.datetime.now().strftime('%m-%d_%H-%M')
    model_path = './models/automm_model_{}'.format(time_str)
    model = MultiModalPredictor(
        label='label',
        problem_type='classification',
        eval_metric='accuracy',
        path=model_path
    )
    model.fit(
        train_data=samples_train,
        holdout_frac=0.2,
        time_limit=None,
        presets='best_quality',
        hyperparameters=training_args
    )
    return model


def evaluate(samples_eval, model):
    outcomes = model.evaluate(samples_eval, metrics='f1', return_pred=True)

    preds, trues = list(outcomes[1].values), samples_eval['label'].to_list()
    
    samples_msg_list = samples_eval['message'].to_list()
    for i in range(len(trues)):
        if preds[i] != trues[i]:
            print('****** Incorrect Prediction:', samples_msg_list[i], trues[i])
    f1, precision, recall = (
        f1_score(trues, preds, average='binary', pos_label='Bad'),
        precision_score(trues, preds, average='binary', pos_label='Bad'),
        recall_score(trues, preds, average='binary', pos_label='Bad')
    )

    print(Fore.LIGHTBLUE_EX, f'****** Fold {current_fold} f1 = {round(f1, 5)} precision = {round(precision, 5)} recall = {round(recall, 5)}', Fore.RESET)
    outcomes[1].to_csv('./data/predictions_{}_{}.csv'.format(
        current_fold, 
        datetime.datetime.now().strftime('%m-%d_%H-%M')))


def main():
    global current_fold
    complete_data = load_dataset(dataset_path)

    kf = KFold(n_splits=NUM_FOLDS, shuffle=True)
    for fold, (train_index, valid_index) in enumerate(kf.split(complete_data)):
        current_fold = fold
        print(Fore.LIGHTGREEN_EX, f'Start training fold {fold}', Fore.RESET)

        data_train = complete_data.iloc[train_index]
        data_eval = complete_data.iloc[valid_index]

        predictor = train(data_train)
        evaluate(data_eval, model=predictor)


if __name__ == '__main__':
    main()
