# coding: utf-8

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

SETTINGS_PATH = 'settings.xml'
TAG_PREVIOUS_LOC = 'ReferenceLoc'
TAG_NEXT_LOC = 'TargetLoc'
TAG_LOC = 'Localizations'



def get_tag_text(root, path):
    return root.find('./{}'.format(path)).text.strip()

#TODO
def check_settings():
    pass


def get_pathes():
    try:
        tree = et.ElementTree(file=SETTINGS_PATH)
    except IOError:
        tree = None
    if tree is not None:
        root = tree.getroot()
        path_to_old_loc = get_tag_text(root, TAG_PREVIOUS_LOC)
        path_to_new_loc = get_tag_text(root, TAG_NEXT_LOC)
    else:
        path_to_old_loc = path_to_new_loc = None
    return path_to_old_loc, path_to_new_loc

def get_list_of_locs():
    try:
        tree = et.ElementTree(file=SETTINGS_PATH)
    except IOError:
        tree = None
    if tree is not None:
        root = tree.getroot()
        list_of_locs = get_tag_text(root, TAG_LOC).split()
    else:
        list_of_locs = None
    return list_of_locs

def main():
    path1, path2 = get_pathes()
    print path1, path2
    localizations = get_list_of_locs()
    print localizations

if __name__ == '__main__':
    main()