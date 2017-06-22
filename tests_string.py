# coding: utf-8

def find_variables(msgstr):
    import re
    # ищет формулы формата %(variable)s или %s или {abc}
    template = re.compile(r'(%(\(\w+\))?[a-zA-Z])|({/?\w+})')
    results = template.findall(msgstr)
    variables = [result[0] or result[2] for result in results]
    return variables


def delete_variables(string):
    clean_string = string
    for variable in find_variables(string):
        clean_string = clean_string.replace(variable, '')
    return clean_string


def is_only_tech_symbols(string):
    tech_symbols = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'0', u'/',
                    u'\\', u'"', u'(', u')', u'{', u'}', u'%', u'!', u'?', u'\n', u'_',
                    u'[', u']', u'#', u':', u';', u'=', u'+', u'*', u'•', u'-', u'–', u' ',
                    u'>', u'<', u'•', u',', u'.']
    clean_string = delete_variables(string)
    letters = list(clean_string)
    # print letters
    for letter in letters:
        if letter not in tech_symbols:
            return False
    return True


# test for equality of msgstr and msgid. msgid must be equalent, msgstr must be different
def equality(string1, string2, **kwargs):
    errors = u''
    string_exceptions = [u'?empty?', u'I', u'II', u'III', u'IV', u'V', u'VI', u'VII', u'VIII', u'IX', u'X']
    # additional exceptions
    if (string1 not in string_exceptions
        and not
        is_only_tech_symbols(string1)):
        if string1 == string2:
            errors = u'&& STRINGS ARE EQUAL '
    return errors


def char_test(string1, string2, **kwargs):
    origin = kwargs.get('first_loc_code') or u'ORIGIN'
    target = kwargs.get('second_loc_code') or u'TARGET'
    chars = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'0',
             u'{', u'}', u'%', u'?', u'\n', u'_', u'[', u']', u'#',  u'=',
             u'+', u'*', u'•',] # "'", '-', ' I ', ' V', ' X ', ':', '/', '\\', '"' too much bugs
    chars_count_main = [0] * len(chars)
    chars_count_sec = [0] * len(chars)
    errors = u''

    for idy, char in enumerate(chars):
        chars_count_main[idy] = string1.count(char)
        chars_count_sec[idy] = string2.count(char)
    if chars_count_main != chars_count_sec:
        modified_chars = []
        for id, char in enumerate(chars):
            if chars_count_main[id] != chars_count_sec[id]:
                modified_chars.append(u'"{}"'.format(chars[id]))
        errors = u'&& COUNT OF SYMBOLS {} '.format(u', '.join(modified_chars))
    # Проверка парности скобок
    str1_count_open_parenthesis = string1.count(u'(')
    str1_count_close_parenthesis = string1.count(u')')
    str2_count_open_parenthesis = string2.count(u'(')
    str2_count_close_parenthesis = string2.count(u')')
    if str1_count_open_parenthesis != str1_count_close_parenthesis:
        errors += u'&& COUNT OF "(" and ")" NOT EQUAL AT {} '.format(origin)
    if str2_count_open_parenthesis != str2_count_close_parenthesis:
        errors += u'&& COUNT OF "(" and ")" NOT EQUAL AT {} '.format(target)
    return errors


def variables_test(string1, string2, **kwargs):
    origin = kwargs.get('first_loc_code') or u'ORIGIN'
    target = kwargs.get('second_loc_code') or u'TARGET'
    errors = ''
    variables_in_first_string = find_variables(string1)
    variables_in_second_string = find_variables(string2)
    # Формируем список отсутствия переменных по принципу несовпадения их количества в листах.
    missed_variables_in_first_string = [variable
                                        for variable in variables_in_second_string
                                        if
                                        (variables_in_first_string.count(variable)
                                        <
                                        variables_in_second_string.count(variable))]
    missed_variables_in_second_string = [variable
                                        for variable in variables_in_first_string
                                        if
                                        (variables_in_second_string.count(variable)
                                        <
                                        variables_in_first_string.count(variable))]
    # Трансформируем в сет, чтобы убрать повторения в листе
    missed_variables_in_first_string = set(missed_variables_in_first_string)
    missed_variables_in_second_string = set(missed_variables_in_second_string)

    if missed_variables_in_first_string:
        errors += u'&& VARIABLE MISSED({}): {} '.format(origin, ', '.join(missed_variables_in_first_string))
    if missed_variables_in_second_string:
        errors += u'&& VARIABLE MISSED({}): {} '.format(target, ', '.join(missed_variables_in_second_string))
    # Проверка на порядок упоминания переменных в строке, большинство не баги, если спамит, закомментировать блок
    # if not missed_variables_in_first_string and not missed_variables_in_second_string:
    #     for i, _ in enumerate(variables_in_first_string):
    #         if variables_in_first_string[i] != variables_in_second_string[i]:
    #             errors += u'&& WRONG ORDER OF VARIABLES(TARGET) '
    #             break
    return errors


def find_fish(string1, string2, **kwargs):
    origin = kwargs.get('first_loc_code') or u'ORIGIN'
    target = kwargs.get('second_loc_code') or u'TARGET'
    errors = ''
    if len(string1)>2:
        if string1.startswith('+') and string1.endswith('+'):
            errors += u'&& FISH TEXT({}) '.format(origin)
    if len(string2) > 2:
        if string2.startswith('+') and string2.endswith('+'):
            errors += u'&& FISH TEXT({}) '.format(target)
    return errors


def find_fish_with_msgid(msgid, msgstr1, msgstr2, **kwargs):
    origin = kwargs.get('first_loc_code') or u'ORIGIN'
    target = kwargs.get('second_loc_code') or u'TARGET'
    errors = ''
    if len(msgid) > 0:
        if msgstr1 == msgid:
            errors += u'&& FISH TEXT({}) '.format(origin)
        if msgstr2 == msgid:
            errors += u'&& FISH TEXT({}) '.format(target)
    return errors


def find_rus(string, **kwargs):
    origin = kwargs.get('first_loc_code') or u'ORIGIN'
    target = kwargs.get('second_loc_code') or u'TARGET'
    errors = ''
    rus_letters = list()
    is_rus_letter_in_string = False
    # Русские символы в unicode находятся с 1040 по 1103 номера
    for i in range(1040, 1104):
        rus_letters.append(unichr(i))
    for letter in rus_letters:
        if letter in string:
            is_rus_letter_in_string = True
            errors += u'&& RUSSIAN SYMBOLS({}):'.format(target)
            break
    if is_rus_letter_in_string:
        for index, letter in enumerate(string):
            if letter in rus_letters:
                errors += u' start position {} '.format(index)
                break
    return errors


