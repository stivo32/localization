# coding: utf-8
try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et
import re
import os.path
import glob

WARNINGS = 'warnings'
CRITICAL = 'critical'
BUGS = 'bugs'

JS_SCRIPT = """
    function change(arg){
        arg.classList.toggle('resolved');
    }
"""


class Filter(object):
    regex = None
    tag = 'special'
    replace_str = '<span class={}>'.format(tag) + '{}</span>'
    style = u'span {color: #2016E2; font-weight: bold; }'

    def __init__(self):
        pass


class FilterDigits(Filter):
    regex = r'\d+'
    tag = 'digit'
    replace_str = '<span class={}>'.format(tag) + '{}</span>'
    style = u'.digit { color: #2016E2; font-weight: bold; }'

    def __init__(self):
        super(FilterDigits, self).__init__()


class FilterVariable(Filter):
    regex = r'(%(\(\w+\))?[a-zA-Z])|({/?\w+})'
    tag = 'variable'
    replace_str = '<span class={}>'.format(tag) + '{}</span>'
    style = u'.variable { color: #2016E2; font-weight: bold; }'

    def __init__(self):
        super(FilterVariable, self).__init__()


class FilterSpecial(Filter):
    regex = r'%+'

    def __init__(self):
        super(FilterSpecial, self).__init__()


class FilterLineBreak(Filter):
    regex = r'\n+'

    def __init__(self):
        super(FilterLineBreak, self).__init__()


class Issue(object):
    def __init__(self, data):
        self.data = data
        self.file = None
        self.msgid = None
        self.issue = None
        self.string_fot_parsing = []
        self.parse()
        self.html_repr()

    def parse(self):
        raise Exception('')

    def html_repr(self):
        self.html = u"""
            <div onclick="change(this);">
                <table>
                    <tr>
                        <td>{issue}</td>
                    <tr>
                    <tr>
                        <td>{file}</td>
                    <tr>
                    <tr>
                        <td>{msgid}</td>
                    <tr>
                    <tr>
                        <td><pre>{msgstrs}</pre></td>
                    <tr>
                </table>
            </div>
                """.format(issue=self.issue,
                           file=self.file,
                           msgid=self.msgid,
                           msgstrs=u'\n'.join(self.string_fot_parsing))

    def __repr__(self):
        return self.html

    def __str__(self):
        return self.html.encode('utf-8')


class Bug(Issue):
    def __init__(self, data):
        super(Bug, self).__init__(data)

    def parse(self):
        split_data = self.data.strip().split('\n')
        self.issue = split_data[0]
        self.file = split_data[1]
        self.msgid = split_data[2]
        for msgstr in split_data[3:]:
            msgstr = make_filters(msgstr)
            self.string_fot_parsing.append(msgstr)


class Warning(Issue):
    def __init__(self, data):
        super(Warning, self).__init__(data)

    def parse(self):
        split_data = self.data.strip().split('\n')
        self.issue = split_data[0]
        self.file = split_data[1]
        self.msgid = split_data[2]
        for msgstr in split_data[3:]:
            msgstr = make_filters(msgstr)
            self.string_fot_parsing.append(msgstr)


class Critical(Issue):
    def __init__(self, data):
        super(Critical, self).__init__(data)

    def parse(self):
        split_data = self.data.strip().split('\n')
        self.issue = split_data[0]
        for msgstr in split_data[1:]:
            self.string_fot_parsing.append(msgstr)

    def html_repr(self):
        self.html = u"""
            <div onclick="change(this);">
                <table>
                    <tr>
                        <td>{issue}</td>
                    <tr>
                    <tr>
                        <td><pre>{msgstrs}</pre></td>
                    <tr>
                </table>
            </div>
                """.format(issue=self.issue,
                           msgstrs=u'\n'.join(self.string_fot_parsing))


def get_root(path):
    try:
        tree = et.ElementTree(file=path)
    except IOError:
        tree = None
    root = tree.getroot()
    return root


def create_html(styles, issues):
    html = """
<html>
    <head>
        <script src="http://code.jquery.com/jquery-latest.js"></script>
        <script>
            {script}
        </script>
        <style>
            {table_style}
            {styles}
            {resolved}
        </style>
    </head>
    <body>
        {issues}
    </body>
</html>
    """.format(
        table_style='div {border-bottom: 2px dashed blue; margin: 30px;}\n',
        styles='\n'.join(styles),
        issues='\n'.join(issues),
        resolved='.resolved {background-color: red;}',
        script=JS_SCRIPT,
    )
    return html


def add_styles():
    styles = list()
    styles.append(Filter.style)
    styles.append(FilterVariable.style)
    styles.append(FilterDigits.style)
    return styles


def get_issues(path):
    with open(path) as file_data:
        data = file_data.read().strip().split('\n\n')
    return [issue.decode('utf-8') for issue in data]


def make_html(path):
    files = glob.glob(os.path.join(path, '*.txt'))
    styles = add_styles()
    issue_classes = {
        'warnings': Warning,
        'bugs': Bug,
        'critical': Critical,
    }
    for file in files:
        file_name = os.path.basename(file)
        loc_code, file_type = file_name.split(".")[0].split("_")
        if issue_classes.get(file_type) is not None:
            html_file_name = file_name.replace('.txt', '.html')
            data = get_issues(file)
            if len(data) <= 1:
                continue
            issues = list()
            for issue in data:
                issues.append(str(issue_classes[file_type](issue)))
            html = create_html(styles, issues)
            with open(os.path.join(path, html_file_name), 'w') as html_file:
                html_file.write('{}'.format(html))
            print 'Created {}'.format(html_file_name)
        else:
            print 'Found wrong .txt  in {}'.format(file)


def make_filters(message):
    pattern = FilterVariable.regex
    template = re.compile(pattern)
    results = template.findall(message)
    variables = [result[0] or result[2] for result in results]
    variables = [FilterVariable.replace_str.format(variable) for variable in variables]
    message = re.sub(pattern, '{}', message)
    filters = [FilterLineBreak, FilterDigits, FilterSpecial]
    for filter in filters:
        message = _make_filter(message, filter)
    message = message.format(*variables)
    return message


def _make_filter(message, current_filter):
    filter_result = re.findall(current_filter.regex, message)
    if current_filter is FilterLineBreak:
        filter_result = ','.join(filter_result).replace('\n', '\\n').split(',')

    if not filter_result:
        return message

    str_in_list = re.split(current_filter.regex, message)
    filter_result = [current_filter.replace_str.format(element) for element in filter_result]
    message = str_in_list[0]
    for i in xrange(1, len(str_in_list)):
        message += filter_result[i-1] + str_in_list[i]
    return message


def main():
    make_html('d:/Repository/QA_new/QA_Integration/Localization_test_branch/Results/JA_Results')


if __name__ == '__main__':
    main()


