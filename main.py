import copy
import csv
import os
import shutil
import stat
from tempfile import NamedTemporaryFile

from git import Repo

dataset_file = './python_dataset.csv'
new_file = './results_dataset.csv'
folder_name = "./current_repository"
temp_file = NamedTemporaryFile('w+t', newline='', delete=False)
result_folder = "./result_folder/"
new_result = []


def get_list():
    list = []
    header = ''
    with open(dataset_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for i, row in enumerate(csv_reader):
            if i is 0:
                header = copy.deepcopy(row)
            else:
                list.append(copy.deepcopy(row))
    return header, list


def set_result(item):
    file1 = open(result_folder + item[0] + '.txt', 'r', encoding="utf8")
    lines = file1.readlines()
    dataline = lines[-2]
    split = dataline.split('│')  # │  (U+2502) is a different symbol than | (U+007C)
    totalcode = split[4].strip()
    totalcomments = split[6].strip()
    commentpercentage = (int(totalcomments) / (int(totalcode) + int(totalcomments))) * 100
    commentpercentage = round(commentpercentage, 1)
    item[2] = totalcode
    item[3] = totalcomments
    item[-1] = commentpercentage
    new_result.append(item)


def download_and_use_repository(item):
    repo = Repo.clone_from(item[1], folder_name)
    # run the system command to use pygount to pull the repository, this step can take a while as some repositories
    # are quite big. Dev note: A repository of 7gb took around 10 minutes of downloading for me and 15 minutes of
    # reading
    os.system(f'pygount {folder_name} --format=summary --out={result_folder + item[0]}.txt')
    # actions done with repository, clear it from the cache and then remove it (needed to fully remove the folder)
    repo.git.clear_cache()

    # make sure that all the read only files inside the folder are handled as can be written, otherwise they persist
    # and error out the entire application
    def del_rw(action, name, exc):
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)

    shutil.rmtree(folder_name, onerror=del_rw)
    set_result(item)


if __name__ == '__main__':
    header, list = get_list()
    new_result.append(header)
    if not os.path.exists(result_folder):
        # Create a new directory because it does not exist
        os.makedirs(result_folder)
    for i, item in enumerate(list):
        if os.path.exists(result_folder + item[0] + ".txt"):
            set_result(item)
        else:
            download_and_use_repository(item)
    writer = csv.writer(temp_file, delimiter=',', quotechar='"')
    for row in new_result:
        writer.writerow(row)
    # for some reason shutil.move throws an error, but still successfully works
    shutil.move(temp_file.name, new_file)
