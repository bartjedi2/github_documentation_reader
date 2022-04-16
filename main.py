import copy
import csv
import os
import shutil
import stat

from git import Repo

folder_name = "./current_repository"
result_folder = "./result_folder/"


def get_list():
    list = []
    header = ''
    with open('./python_dataset.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for i, row in enumerate(csv_reader):
            if i is 0:
                header = copy.deepcopy(row)
            else:
                list.append(copy.deepcopy(row))
    return header, list


def download_and_use_repository(item):
    repo = Repo.clone_from(item[1], folder_name)
    print("download finished")
    # run the system command to use pygount to pull the repository, this step can take a while as some repositories are quite big.
    # Dev note: A repository of 7gb took around 10 minutes for me
    os.system(f'pygount {folder_name} --format=summary --out={result_folder + item[0]}.txt')
    print("analysis finished;llll")
    # actions done with repository, clear it from the cache and then remove it (needed to fully remove the folder)
    repo.git.clear_cache()
    # make sure that all the read only files inside the folder are handled as can be written, otherwise they persist
    # and error out the entire application
    def del_rw(action, name, exc):
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)
    shutil.rmtree(folder_name, onerror=del_rw)


if __name__ == '__main__':
    header, list = get_list()
    if not os.path.exists(result_folder):
        # Create a new directory because it does not exist
        os.makedirs(result_folder)
    for i, item in enumerate(list):
        print("start " + item[0])
        download_and_use_repository(item)
        print("finished " + item[0])
