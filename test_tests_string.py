# coding: utf-8
import tests_string


def test_find_fish():
    string1 = u'+s+'
    string2 = u''
    assert tests_string.find_fish(string1, string2) == u'&& FISH TEXT(ORIGIN) '
    string1 = u''
    string2 = u'+s+'
    assert tests_string.find_fish(string1, string2) == u'&& FISH TEXT(TARGET) '
    string1 = string2 = u'+s+'
    assert tests_string.find_fish(string1, string2) == u'&& FISH TEXT(ORIGIN) && FISH TEXT(TARGET) '
    string1 = string2 = u''
    assert tests_string.find_fish(string1, string2) == u''

def test_find_fish_with_msgid():
    string = u''
    assert tests_string.find_fish_with_msgid(string, string, string) == u''
    msgid = u'sometext'
    string1 = u'sometext'
    string2 = u'anothertext'
    assert tests_string.find_fish_with_msgid(msgid, string1, string2) == u'&& FISH TEXT(ORIGIN) '
    assert tests_string.find_fish_with_msgid(msgid, string2, string1) == u'&& FISH TEXT(TARGET) '
    assert tests_string.find_fish_with_msgid(msgid, string1, string1) == u'&& FISH TEXT(ORIGIN) && FISH TEXT(TARGET) '

def test_find_rus():
    char = unichr(1039) # Before russian A
    assert tests_string.find_rus(char) == u''
    char = unichr(1104) # After russian я
    assert tests_string.find_rus(char) == u''
    char = unichr(1040) # А
    assert tests_string.find_rus(char) == u'&& RUSSIAN SYMBOLS(TARGET_NEW_LOC): start position 0 '
    char = unichr(1103) # я
    assert tests_string.find_rus(char) == u'&& RUSSIAN SYMBOLS(TARGET_NEW_LOC): start position 0 '
    char = u'A' # ASCII A
    assert tests_string.find_rus(char) == u''
    char = u'z' # ASCII A
    assert tests_string.find_rus(char) == u''

def test_find_variables():
    string = u'abc'
    assert tests_string.find_variables(string) == []
    string = u'%s'
    assert tests_string.find_variables(string) == [u'%s']
    string = u'%(variable)c'
    assert tests_string.find_variables(string) == [u'%(variable)c']
    string = u'%%'
    assert tests_string.find_variables(string) == []
    string = u'%(variable(c'
    assert tests_string.find_variables(string) == []
    string = u'%(%s)s'
    assert tests_string.find_variables(string) == [u'%s']
    string = u'%(variable)s%f'
    assert tests_string.find_variables(string) == [u'%(variable)s', u'%f']
    string = u'%русский'
    assert tests_string.find_variables(string) == []

def test_delete_variables():
    string = u'abc'
    assert tests_string.delete_variables(string) == u'abc'
    string = u''
    assert tests_string.delete_variables(string) == u''
    string = u'%s'
    assert tests_string.delete_variables(string) == u''
    string = u'%(variable)s'
    assert tests_string.delete_variables(string) == u''
    string = u'надпись%(variable)s, %sнадпись'
    assert tests_string.delete_variables(string) == u'надпись, надпись'
    string = u'надпись%(variable)s, %(variable)sнадпись'
    assert tests_string.delete_variables(string) == u'надпись, надпись'

def test_equality():
    string_exceptions = [u'?empty?', u'I', u'II', u'III', u'IV', u'V', u'VI', u'VII', u'VIII', u'IX', u'X']
    for string in string_exceptions:
        assert tests_string.equality(string, string) == u''
    string = u''
    assert tests_string.equality(string, string) == u''
    string = u'ascii'
    assert tests_string.equality(string, string) == u'&& STRINGS ARE EQUAL '
    string = u'юникод'
    assert tests_string.equality(string, string) == u'&& STRINGS ARE EQUAL '
    string = u'123456'
    assert tests_string.equality(string, string) == u''
    string1 = u'abc%sabc'
    string2 = u'abc%iabc'
    assert tests_string.equality(string1, string2) == u''

def test_is_only_tech_symbols():
    tech_symbols = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'0', u'/',
                    u'\\', u'"', u'(', u')', u'{', u'}', u'%', u'!', u'?', u'\n', u'_',
                    u'[', u']', u'#', u':', u';', u'=', u'+', u'*', u'•', u'-', u'–', u' ',
                    u'>', u'<', u'•', u',', u'.']
    string = u'%s%(value)s'
    string += u''.join(tech_symbols)
    assert tests_string.is_only_tech_symbols(string)
    string = u''
    assert tests_string.is_only_tech_symbols(string)
    string = u'abc'
    assert tests_string.is_only_tech_symbols(string) is False

def test_char_test():
    chars = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'0',
             u'{', u'}', u'%', u'?', u'\n', u'_', u'[', u']', u'#', u'=',
             u'+', u'*', u'•', ]
    string1 = u''
    string2 = u''
    assert tests_string.char_test(string1, string2) == u''
    string1 = chars[0]
    string2 = u''
    assert tests_string.char_test(string1, string2) == u'&& COUNT OF SYMBOLS "{}" '.format(chars[0])
    string1 = chars[1]
    string2 = chars[1]
    assert tests_string.char_test(string1, string2) == u''
    string1 = u'('
    string2 = u')'
    assert tests_string.char_test(string1, string2) == u'&& COUNT OF "(" and ")" NOT EQUAL AT ORIGIN && COUNT' \
                                                       u' OF "(" and ")" NOT EQUAL AT TARGET '

def test_variables_test():
    string1 = u''
    string2 = u''
    assert tests_string.variables_test(string1, string2) == u''
    string1 = u'%s'
    string2 = u''
    assert tests_string.variables_test(string1, string2) == u'&& VARIABLE MISSED(TARGET): {} '.format(string1)
    assert tests_string.variables_test(string2, string1) == u'&& VARIABLE MISSED(ORIGIN): {} '.format(string1)
    string1 = u'%s'
    string2 = u'%s'
    assert tests_string.variables_test(string2, string1) == u''
    string1 = u'%s'
    string2 = u'%i'
    assert tests_string.variables_test(string1, string2) == u'&& VARIABLE MISSED(ORIGIN): {} && VARIABLE' \
                                                            u' MISSED(TARGET): {} '.format(string2, string1)
    string1 = u'%s%s'
    string2 = u'%s'
    assert tests_string.variables_test(string1, string2) == u'&& VARIABLE MISSED(TARGET): {} '.format(u'%s')
    string1 = u'%s%i'
    string2 = u'%i%s'
    assert tests_string.variables_test(string1, string2) == u'&& WRONG ORDER OF VARIABLES(TARGET) '










