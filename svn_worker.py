import os
import subprocess


def download_loc(loc_path, revision, output_folder_name_in_cur_path):
    # #create output folder if not exist
    # if output_folder_name_in_cur_path not in os.listdir(os.getcwd()):
    #     os.mkdir(output_folder_name_in_cur_path)
    # #remove old files
    # files = os.listdir(output_folder_name_in_cur_path)
    # for file in files:
    #     if file != '.svn':
    #         os.remove(output_folder_name_in_cur_path + '/' + file)
    #download new files
    # URL = 'https://svn-by.wargaming.net/svn/wotdev/localize/media/client/' + version_code_loc_path + '/text'
    URL = 'https://svn-by.wargaming.net/svn/wotdev/' + loc_path + '/text'
    PATH = os.getcwd() + '/' + output_folder_name_in_cur_path + '/'
    rev = revision
    subprocess.call('svn checkout --depth files' + ' ' + '-r ' + str(rev) + ' ' + URL + ' ' + PATH)

