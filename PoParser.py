# coding: utf-8
import re

MSGID_MARKER = 'msgid|MSGID'
MSGSTR_MARKER = 'msgstr|MSGSTR'
MSG_END = '"\n'

class PoEntry:
    def __init__(self, msgid, msgstr):
        self.msgid = msgid
        self.msgstr = msgstr

    def __str__(self):
        return str(self.msgid)

    def __repr__(self):
        return self.msgid

    def encode(self, codec):
        return self.msgid.encode(codec)

    def get_raw_entry(self):
        return str(('msgid "' + self.msgid + '"' + '\n' + 'msgstr "' + self.msgstr + '"' + '\n').encode('utf-8', errors='ignore'))


class PoFile:
    def __init__(self):
        self.added_entrys = [] # for instances containing diff between two po files
        self.deleted_entrys = [] # for instances containing diff between two po files
        self.modified_entrys = []  # for instances containing diff between two po files
        self.entries = []
        self.msgid_index = []
        self.msgstr_index = []
        self.path = ''

    def __getitem__(self, key):
        return self.entries[key]

    def add_entry(self, entry):
        self.entries.append(entry)
        self.msgid_index.append(entry.msgid)
        self.msgstr_index.append(entry.msgstr)

    def __len__(self):
        return len(self.entries)

    def make_raw_file(self, path_to_out, add_info):
        with open(path_to_out, 'w') as raw_file:
            for entry in self:
                raw_file.write(entry.get_raw_entry() + '\n')
                raw_file.write('')
            if add_info != 0:
                raw_file.write('----------strings affected----------' + '\n')
                for line in self.make_diff_info():
                    raw_file.write(line.encode('utf-8', errors='ignore'))

    def make_diff_info(self):
        diff_info = []
        for entry in self.modified_entrys:
            diff_info.append('*modified string of msgid "' + entry.msgid + '"' + '\n')
        for entry in self.deleted_entrys:
            diff_info.append('*deleted msgid  "' + entry.msgid + '"' + '\n')
        for entry in self.added_entrys:
            diff_info.append('*added msgid "' + entry.msgid + '"' + '\n')
        return diff_info

    def path(self):
        return self.path

    def return_msgstr(self, msgid):
        for idx, _ in enumerate(self.msgid_index):
            if msgid == self.msgid_index[idx]:
                return self.msgstr_index[idx]
        return 'None'

def get_content(msg):
    # Выделяем текст внутри кавычек
    pattern = re.compile('\"(.*)\"')
    return pattern.search(msg).group(1)

def is_msgid(msg):
    pattern = re.compile('^\s*(msgid|MSGID)\s*".*"\s*$')
    quotes = msg.count('"') - msg.count('\\"')
    return True if (pattern.search(msg) is not None and quotes == 2) else False

def is_msgstr(msg):
    pattern = re.compile('^\s*(msgstr|MSGSTR)\s*".*"\s*$')
    quotes = msg.count('"') - msg.count('\\"')
    return True if (pattern.search(msg) is not None and quotes == 2) else False

def make_pofile(path):
    po = PoFile()
    po.path = path
    file_lines = []
    try:
        with open(path, 'r') as po_file:
            for i, line in enumerate(po_file):
                if re.search(MSGID_MARKER, line) or re.search(MSGSTR_MARKER, line):
                    file_lines.append(line.decode('utf-8', errors='ignore'))
    except IOError:
        pass
    clean_msgid = []
    clean_msgstr = []
    for idx, line in enumerate(file_lines):
        if is_msgid(line):
            if is_msgstr(file_lines[idx+1]):
                clean_msgid.append(get_content(line))
                clean_msgstr.append(get_content(file_lines[idx+1]))
            else:
                error_message = u'PO ERROR: SOMETHING IS WRONG WITH MSGID  {} from {}\n'.format(line[:-1],path)
                with open('Results/errors.log', 'a') as errors:
                    errors.write(error_message.encode('utf-8', errors='ignore'))
    for number, line in enumerate(clean_msgid):
        po.add_entry(PoEntry(clean_msgid[number], clean_msgstr[number]))
    return po




# make PoFile instance with diff between file1 and file2
def make_diff_pofile(path1, path2):
    if path1 is None:
        po1 = PoFile() # creates empty PoFile instance
    else:
        po1 = make_pofile(path1)
    po2 = make_pofile(path2)
    diff_po = PoFile()
    for entry in po1:
        if entry.msgid not in po2.msgid_index:
            diff_po.deleted_entrys.append(entry)
    for entry in po2:
        if entry.msgid not in po1.msgid_index:
            diff_po.added_entrys.append(entry)
            diff_po.add_entry(entry)
        else:
            if entry.msgstr != po1.return_msgstr(entry.msgid):
                diff_po.modified_entrys.append(entry)
                diff_po.add_entry(entry)
    return diff_po
