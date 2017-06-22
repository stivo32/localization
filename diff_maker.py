# coding: utf-8

import PoParser
import tests_string
import os
import shutil
import xml_reader
import time
import make_html
import glob

FOLDER_FOR_RESULTS = 'Results'
if os.path.exists('C:/Program Files (x86)/Beyond Compare 4/BCompare.exe'):
    PATH_TO_BEYOND_COMPARE = 'C:/"Program Files (x86)"/"Beyond Compare 4"/BCompare.exe'
else:
    PATH_TO_BEYOND_COMPARE = 'C:/"Program Files"/"Beyond Compare 4"/BCompare.exe'
# first_loc_code = 'first'
# second_loc_code = 'second'


def make_po_files_list(path):
    po_list = []
    files = os.listdir(path)
    for line in files:
        if line.endswith('.po'):
            po_list.append(line)
    return po_list


def make_diff_files(old_loc, new_loc, po_list_old, po_list_new, diff_path, pathes):
    deleted_files = []
    added_files = []
    # create list of deleted files
    for po_file in po_list_old:
        if po_file not in po_list_new:
            deleted_files.append(po_file)
    # create deleted.txt
    with open(os.path.join(diff_path, 'deleted_files.txt'), 'w') as del_files:
        for line in deleted_files:
            line = line.encode('utf-8', errors='ignore')
            del_files.write(line + '\n')
    # create list of added files
    for po_file in po_list_new:
        if po_file not in po_list_old:
            added_files.append(po_file)
    # create added.txt
    with open(os.path.join(diff_path, 'added_files.txt'), 'w') as ad_files:
        for line in added_files:
            line = line.encode('utf-8', errors='ignore')
            ad_files.write(line + '\n')
    # create added_diff files with full "added" info
    for po_file in added_files:
        added_po = PoParser.make_diff_pofile(None, os.path.join(new_loc, po_file))
        added_po.make_raw_file(os.path.join(diff_path, po_file), 1)
    # make diffs files
    for po_file in po_list_new:
        if po_file in po_list_old:
            diff_po = PoParser.make_diff_pofile(os.path.join(old_loc, po_file), os.path.join(new_loc, po_file))
            # put file in output/main diffs files
            diff_po.make_raw_file(os.path.join(diff_path, po_file), 1)


# TODO выяснить куда делся deleted.txt
def make_version_test(pathes, check_rus_symbols=False):
    critical = []
    warnings = []
    bugs = []
    first_old_loc = pathes['first_old_loc']
    first_new_loc = pathes['first_new_loc']
    second_old_loc = pathes['second_old_loc']
    second_new_loc = pathes['second_new_loc']
    first_diff = pathes['first_diff']
    second_diff = pathes['second_diff']

    # make loc1_1 - 1_2 diff files.po and put it into 'output/main_diff files
    po_list_first_old = make_po_files_list(first_old_loc)
    po_list_first_new = make_po_files_list(first_new_loc)
    po_list_second_old = make_po_files_list(second_old_loc)
    po_list_second_new = make_po_files_list(second_new_loc)
    pathes['po_list_first_old'] = po_list_first_old
    pathes['po_list_first_new'] = po_list_first_new
    pathes['po_list_second_old'] = po_list_second_old
    pathes['po_list_second_new'] = po_list_second_new

    loc_codes = dict()
    loc_codes['first_loc_code'] = pathes['first_loc_code']
    loc_codes['second_loc_code'] = pathes['second_loc_code']

    main_deleted_files = []
    main_added_files = []
    sec_deleted_files = []
    sec_added_files = []

    make_diff_files(first_old_loc, first_new_loc, po_list_first_old, po_list_first_new, first_diff, pathes)
    make_diff_files(second_old_loc, second_new_loc,  po_list_second_old, po_list_second_new, second_diff, pathes)

    # compare deleted and added files in main and sec
    with open('/'.join([first_diff, 'deleted_files.txt']), 'r') as del_files:
        for file in del_files:
            main_deleted_files.append(file[:-1]) #[:-1] - for delete \n
    with open('/'.join([first_diff, 'added_files.txt']), 'r') as ad_files:
        for file in ad_files:
            main_added_files.append(file[:-1])
    with open('/'.join([second_diff, 'deleted_files.txt']), 'r') as del_files:
        for file in del_files:
            sec_deleted_files.append(file[:-1])
    with open('/'.join([second_diff, 'added_files.txt']), 'r') as ad_files:
        for file in ad_files:
            sec_added_files.append(file[:-1])
    if main_deleted_files != sec_deleted_files:
        critical.append(
            u"""CRITICAL: deleted files in {0} loc and {1} loc are not equal
files have been deleted in {0} loc: [{2}]
files have been deleted in {1} loc: [{3}]""".format(pathes['first_loc_code'],
           pathes['second_loc_code'],
           ', '.join(main_deleted_files),
           ', '.join(sec_deleted_files),
           ))
        if main_added_files != sec_added_files:
            critical.append(
                u"""CRITICAL: added files in {0} loc and {1} loc are not equal
files have been added in {0} loc: [{2}]
files have been added in {1} loc: [{3}]""".format(pathes['first_loc_code'],
               pathes['second_loc_code'],
               ', '.join(main_added_files),
               ', '.join(sec_added_files)
               ))
        #print critical
    # diff file lists in main_new and sec_new.
    # Double check of "compare deleted and added files in main and sec" in normal situation
    # for file in po_list_first_new:
    #     if file not in po_list_second_new:
    #         critical.append(u'CRITICAL: file {} exist only in {}_NEW'.format(file, pathes['first_loc_code']))
    # for file in po_list_second_new:
    #     if file not in po_list_first_new:
    #         critical.append(u'CRITICAL: file {} exist only in {}_NEW'.format(file, pathes['second_loc_code']))
    # make absolute tests with generated diffs

    translate_test_ignored = ['artefacts.po', 'ussr_tankmen.po', 'usa_tankmen.po', 'sweden_tankmen.po',
                              'japan_tankmen.po', 'germany_tankmen.po', 'gb_tankmen.po', 'france_tankmen.po',
                              'czech_tankmen.po', 'china_tankmen.po',
                              'ussr_vehicles.po', 'usa_vehicles.po', 'sweden_vehicles.po',
                              'japan_vehicles.po', 'germany_vehicles.po', 'gb_vehicles.po', 'france_vehicles.po',
                              'czech_vehicles.po', 'china_vehicles.po', 'igr_vehicles.po', 'readable_key_names.po',
                              'vehicle_customization_cn.po', 'development.po'
                              ]
    po_with_description = [
        'ussr_vehicles.po', 'usa_vehicles.po', 'sweden_vehicles.po',
        'japan_vehicles.po', 'germany_vehicles.po', 'gb_vehicles.po',
        'france_vehicles.po', 'czech_vehicles.po', 'china_vehicles.po',
        'igr_vehicles.po'
    ]
    po_list_main = make_po_files_list(first_diff)
    po_list_sec = make_po_files_list(second_diff)

    def get_info(path_to_file):
        info = []
        with open(path_to_file, 'r') as target_file:
            for string in target_file:
                if string.startswith('*'):
                    info.append(string[1:])
        return info

    for file in po_list_main:
        if file in po_list_sec:

            main_file_info = get_info('/'.join([first_diff, file]))
            sec_file_info = get_info('/'.join([second_diff, file]))
            if main_file_info != sec_file_info:

                po_instance_old_main = PoParser.make_pofile('/'.join([first_old_loc, file]))
                po_instance_new_main = PoParser.make_pofile('/'.join([first_new_loc, file]))
                po_instance_old_sec = PoParser.make_pofile('/'.join([second_old_loc, file]))
                po_instance_new_sec = PoParser.make_pofile('/'.join([second_new_loc, file]))
                # Рядом с ворнингами выводим все 4 возможные строки
                # TODO сделано ниразу не красиво, переделать по возможности



                def get_msgid_from_info_string(info_string):
                    import re
                    return re.search('(msgid|MSGID)\s*"(.*)"', info_string).group(2)

                for info_string in main_file_info:
                    po_files_in_resources = []
                    msgid = get_msgid_from_info_string(info_string)
                    if info_string not in sec_file_info:
                        if file in po_list_first_old:
                            po_files_in_resources.append(u'{}_OLD msgstr "{}"\n'.format(pathes['first_loc_code'],
                                                                                po_instance_old_main.return_msgstr(msgid)))
                        if file in po_list_first_new:
                            po_files_in_resources.append(u'{}_NEW msgstr "{}"\n'.format(pathes['first_loc_code'],
                                                                                po_instance_new_main.return_msgstr(msgid)))
                        if file in po_list_second_old:
                            po_files_in_resources.append(u'{}_OLD msgstr "{}"\n'.format(pathes['second_loc_code'],
                                                                                po_instance_old_sec.return_msgstr(msgid)))
                        if file in po_list_second_new:
                            po_files_in_resources.append(u'{}_NEW msgstr "{}"\n'.format(pathes['second_loc_code'],
                                                                                po_instance_new_sec.return_msgstr(msgid)))
                        bug_message = u'WARNING: modified string only in {}\n{}\nmsgid "{}"\n'.format(pathes['first_loc_code'],
                                                                                                          file, msgid)
                        for message in po_files_in_resources:
                            bug_message += message
                        warnings.append(bug_message)

                for info_string in sec_file_info:
                    po_files_in_resources = []
                    msgid = get_msgid_from_info_string(info_string)
                    if info_string not in main_file_info:
                        if file in po_list_first_old:
                            po_files_in_resources.append(u'{}_OLD msgstr "{}"\n'.format(pathes['first_loc_code'],
                                                                                po_instance_old_main.return_msgstr(msgid)))
                        if file in po_list_first_new:
                            po_files_in_resources.append(u'{}_NEW msgstr "{}"\n'.format(pathes['first_loc_code'],
                                                                                po_instance_new_main.return_msgstr(msgid)))
                        if file in po_list_second_old:
                            po_files_in_resources.append(u'{}_OLD msgstr "{}"\n'.format(pathes['second_loc_code'],
                                                                                po_instance_old_sec.return_msgstr(msgid)))
                        if file in po_list_second_new:
                            po_files_in_resources.append(u'{}_NEW msgstr "{}"\n'.format(pathes['second_loc_code'],
                                                                                po_instance_new_sec.return_msgstr(msgid)))
                        bug_message = u'WARNING: modified string only in {}\n{}\nmsgid "{}"\n'.format(pathes['second_loc_code'],
                                                                                                      file, msgid)

                        for message in po_files_in_resources:
                                bug_message += message
                        warnings.append(bug_message)
    for po_file in po_list_main:
        if po_file in po_list_sec:
            # создаем Po каждого файла со списками айдишек и строк
            po_instance_main = PoParser.make_pofile('/'.join([first_new_loc, po_file]))
            po_instance_sec = PoParser.make_pofile('/'.join([second_diff, po_file]))
            for idx, _ in enumerate(po_instance_main.msgid_index):
                cur_msgid = po_instance_main.msgid_index[idx]
                if po_instance_main.msgid_index[idx] in po_instance_sec.msgid_index:
                    # do tests with msgstrings
                    main_msgstr = po_instance_main.return_msgstr(cur_msgid)
                    sec_msgstr = po_instance_sec.return_msgstr(cur_msgid)
                    string_errors = ''
                    string_errors += tests_string.variables_test(main_msgstr, sec_msgstr, **loc_codes)
                    if po_file not in translate_test_ignored:
                        string_errors += tests_string.equality(main_msgstr, sec_msgstr)
                    # Проверяем
                    if po_file in po_with_description and u'_descr' in cur_msgid:
                        string_errors += tests_string.equality(main_msgstr, sec_msgstr)
                    string_errors += tests_string.char_test(main_msgstr, sec_msgstr, **loc_codes)
                    string_errors += tests_string.find_fish(main_msgstr, sec_msgstr, **loc_codes)
                    string_errors += tests_string.find_fish_with_msgid(cur_msgid, main_msgstr, sec_msgstr, **loc_codes)
                    if check_rus_symbols:
                        string_errors += tests_string.find_rus(sec_msgstr, **loc_codes)

                    # if errors, make errors list for msgid
                    if string_errors != '':
                        # bugs.append(string_errors)
                        bugs.append(u'{}\n{}\nmsgid "{}"\n{} msgstr "{}"\n{} msgstr "{}"'.format(string_errors,
                                                                    po_file, cur_msgid,
                                                                    pathes['first_loc_code'], main_msgstr,
                                                                    pathes['second_loc_code'], sec_msgstr))
    return critical, warnings, bugs


def make_mo(po_path, path_to_create_mo):
    if not os.path.exists(path_to_create_mo):
        os.mkdir(path_to_create_mo)

    po_list = [po_file for po_file in os.listdir(po_path) if po_file.endswith('.po')]
    abs_path_to_mo_builder = os.path.join(os.path.abspath('.'), 'bin/msgfmt.exe')

    for po_file in po_list:
        mo_file = po_file.replace('.po', '.mo')
        path_to_mo_file = os.path.join(path_to_create_mo, mo_file)
        path_to_po_files = os.path.join(po_path, po_file)
        os.system('{} -o {} {}'.format(abs_path_to_mo_builder, path_to_mo_file, path_to_po_files))


def check_mo_relevance(path_to_mo_origin, path_to_mo_created):
    mo_list_origin = [mo_file for mo_file in os.listdir(path_to_mo_origin)]
    mo_list_created = [mo_file for mo_file in os.listdir(path_to_mo_created)]
    flag_for_beyond_compare = False
    if mo_list_origin != mo_list_created:
        flag_for_beyond_compare = True
    else:
        mo_list = list(set(mo_list_origin) | set(mo_list_created))
        for mo_file in mo_list:
            try:
                with open(os.path.join(path_to_mo_origin, mo_file)) as mo_origin:
                    with open(os.path.join(path_to_mo_created, mo_file)) as mo_created:
                        mo_origin_data = mo_origin.read()
                        mo_created_data = mo_created.read()
            except IOError:
                flag_for_beyond_compare = True
                break
            if mo_origin_data != mo_created_data:
                flag_for_beyond_compare = True
                break
    if flag_for_beyond_compare:
        print "Something wrong with MO files...Please check in beyond compare"
        # open_beyond_compare(path_to_mo_origin, path_to_mo_created)
    else:
        print 'MO files are relevant'


def get_output_pathes(results_root, first_loc_code, second_loc_code):
    root = os.path.join(results_root, second_loc_code + '_' + FOLDER_FOR_RESULTS)
    first_diff = os.path.join(root, first_loc_code + '_diff')
    second_diff = os.path.join(root, second_loc_code + '_diff')
    second_mo_test = os.path.join(root, second_loc_code + '_test_mo')
    mo_origin = os.path.join(second_mo_test, 'mo')
    mo_created = os.path.join(second_mo_test, 'mo_created')
    return root, first_diff, second_diff, second_mo_test, mo_origin, mo_created


def make_cleanup(results_root):
    if not os.path.exists(results_root):
        os.mkdir(results_root)
    error_log_path = os.path.join(results_root, 'errors.log')
    if os.path.exists(error_log_path):
        os.remove(error_log_path)
    dirs = os.walk(results_root)
    dirs = list(dirs)[0][1]
    for dir in dirs:
        if os.path.exists(os.path.join(results_root, dir)):
            shutil.rmtree(os.path.join(results_root, dir))


def create_folders(pathes):
    os.mkdir(pathes['root'])
    os.mkdir(pathes['first_diff'])
    os.mkdir(pathes['second_diff'])
    os.mkdir(pathes['second_mo_test'])
    os.mkdir(pathes['mo_origin'])
    os.mkdir(pathes['mo_created'])


def write_bugs_into_file(path, fname, bugs):
    with open(os.path.join(path, fname), 'w') as b:
        for line in bugs:
            line = line.encode('utf-8', errors='ignore')
            b.write(line + '\n\n')


def open_beyond_compare(path1, path2):
    path1 = os.path.abspath(path1) + '\\'
    path2 = os.path.abspath(path2) + '\\'
    os.system('{} {} {}'.format(PATH_TO_BEYOND_COMPARE, path1, path2))


def get_reference_loc(target_log):
    compare_with_ru = ('EN', 'UK', 'BE', 'KK')
    compare_with_en = ('BG', 'CS', 'DA', 'DE', 'EL', 'ES', 'ES_AR', 'ES_MX', 'ET', 'FI', 'FIL', 'FR', 'HR', 'HU',
                       'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'MS', 'NL', 'NO', 'PL', 'PT', 'PT_BR', 'RO', 'SR',
                       'SV', 'TH', 'TR', 'VI', 'ZH_CN', 'ZH_SG', 'ZH_TW')
    compare_with_dev = ('RU',)
    link_between_locs = dict()
    link_between_locs['RU'] = compare_with_ru
    link_between_locs['EN'] = compare_with_en
    link_between_locs['DEV'] = compare_with_dev
    for ref, targets in link_between_locs.items():
        if target_log in targets:
            return ref
    return None


def is_folder_exist(path):
    return True if os.path.exists(path) else False


def mo_copy(input_path, output_path):
    mo_list = os.listdir(input_path)
    for mo_file in mo_list:
        if mo_file.endswith('.mo'):
            shutil.copy(os.path.join(input_path, mo_file), output_path)


def cleaner_empty_po(path):
    files = [os.path.basename(file) for file in glob.glob(path+'/*.po')]
    for po_file in files:
        full_path = os.path.join(path, po_file)
        with open(full_path) as po:
            data = po.readlines()
        if len(data) == 1:
            os.remove(full_path)


def make_test_with_loc(results_root, target_loc):

    second_loc_code = target_loc
    first_loc_code = get_reference_loc(second_loc_code)

    pathes = dict()

    print '{} <- {}'.format(first_loc_code, second_loc_code)
    start = time.time()
    path_to_old_loc, path_to_new_loc = xml_reader.get_pathes()
    first_old_loc = os.path.join(path_to_old_loc, first_loc_code, 'text')
    first_new_loc = os.path.join(path_to_new_loc, first_loc_code, 'text')
    second_old_loc = os.path.join(path_to_old_loc, second_loc_code, 'text')
    second_new_loc = os.path.join(path_to_new_loc, second_loc_code, 'text')
    root, first_diff, second_diff, second_mo_test, mo_origin, mo_created = get_output_pathes(results_root,
                                                                                             first_loc_code,
                                                                                             second_loc_code)
    pathes['results_root'] = results_root
    pathes['path_to_old_loc'] = path_to_old_loc
    pathes['path_to_new_loc'] = path_to_new_loc
    pathes['first_loc_code'] = first_loc_code
    pathes['second_loc_code'] = second_loc_code
    pathes['first_old_loc'] = first_old_loc
    pathes['first_new_loc'] = first_new_loc
    pathes['second_old_loc'] = second_old_loc
    pathes['second_new_loc'] = second_new_loc
    pathes['root'] = root
    pathes['first_diff'] = first_diff
    pathes['second_diff'] = second_diff
    pathes['second_mo_test'] = second_mo_test
    pathes['mo_origin'] = mo_origin
    pathes['mo_created'] = mo_created

    loc_pathes = [first_old_loc, first_new_loc, second_old_loc, second_new_loc]
    for loc in loc_pathes:
        if not is_folder_exist(loc):
            print "Path {} doesn't exist. Please check you localizations and try again.\n".format(loc)
            exit()
    create_folders(pathes)
    check_rus_symbols = True if second_loc_code not in ['BG', 'BE', 'UK', 'KK', 'RU'] else False
    print 'Find rus symbols in target localization? {}'.format(check_rus_symbols)
    print 'Doing tests...'
    critical, warnings, bugs = make_version_test(pathes, check_rus_symbols)
    write_bugs_into_file(pathes['root'], '{}_bugs.txt'.format(pathes['second_loc_code']), bugs)
    write_bugs_into_file(pathes['root'], '{}_critical.txt'.format(pathes['second_loc_code']), critical)
    write_bugs_into_file(pathes['root'], '{}_warnings.txt'.format(pathes['second_loc_code']), warnings)
    print 'Creating mo files...'
    mo_copy(pathes['second_new_loc'] + '\LC_MESSAGES', pathes['mo_origin'])
    make_mo(pathes['second_new_loc'], pathes['mo_created'])
    print 'Checking if mo files are relevant...'
    check_mo_relevance(pathes['mo_origin'], pathes['mo_created'])
    # print 'Opening diffs in beyond compare'
    # open_beyond_compare(pathes['first_diff'], pathes['second_diff'])
    print 'Tests finished.'
    print 'Spent time: {} sec'.format(int(time.time() - start))
    print 'Making html files'
    make_html.make_html(pathes['root'])
    cleaner_empty_po(pathes['first_diff'])
    cleaner_empty_po(pathes['second_diff'])


def main():
    results_root = 'Results'
    make_cleanup(results_root)
    locs = xml_reader.get_list_of_locs()
    for loc in locs:
        make_test_with_loc(results_root, loc)
    raw_input('Enter any key to exit')


if __name__ == '__main__':
    main()

