import cv2
import pytesseract
from PIL import Image
import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

day_exp = "([1-3]{0,1}[0-9]{1})"
month_exp = "(January|February|March|April|May|June|July|August|September|October|November|December)"
year_exp = "(|2020|2019)"
ctype_exp = "(Incoming|Outgoing|Missed)"
time_exp = "([0-1][0-9]|2[0-3]):([0-5][0-9])"
duration_exp = "([0-1]{0,1}[:]{0,1}[0-9]{1,2}:[0-5][0-9]|Not answered)"
memory_exp = "([0-9]* *kB|[0-9]*.[0-9] *MB)"

patterns = {
    'pcnd' : re.compile(' *'.join([ctype_exp, duration_exp]) + '$'),
    'pc' : re.compile(ctype_exp + '$'),
    'pd' : re.compile(duration_exp + '$'),
    'ptnm' : re.compile(' *'.join([time_exp, memory_exp]) + '$'),
    'pt' : re.compile(time_exp + '$'),
    'pm' : re.compile(memory_exp + '$'),
}


def match_pattern(line_type, line):
    return bool(re.match(patterns['p{}'.format(line_type)], line))


def matched_pattern(lt_arr, line):
    for lt in lt_arr:
        if match_pattern(lt, line):
            return lt

    return 'u'


def get_line_type(line, prior_type):

    # gets the line type based on conformance with a regexp and the previous line type
    if prior_type == '':
        return matched_pattern(['c', 'cnd'], line)

    if prior_type == 'cnd':
        return matched_pattern(['tnm', 't', 'cnd'], line)

    if prior_type == 'c':
        return matched_pattern(['t'], line)

    if prior_type == 't':
        return matched_pattern(['c', 'd'], line)

    if prior_type == 'd':
        return matched_pattern(['d', 'm'], line)

    if prior_type == 'm':
        return matched_pattern(['d'], line)

    if prior_type == 'tnm':
        return matched_pattern(['cnd'], line)

    if prior_type == 'u':
        return matched_pattern(['c', 'cnd', 't', 'd', 'm', 'tnm'], line)

    return 'u'


def extract_name(sarr):
    return sarr[0]


def get_format_type(sarr):
    p1 = re.compile(' *'.join([ctype_exp, duration_exp]) + '$')
    p2 = re.compile(' *'.join([time_exp, memory_exp]) + '$')
    cnd_arr = [x for x in sarr if bool(re.match(p1, x.strip()))]
    tnm_arr = [x for x in sarr if bool(re.match(p2, x.strip()))]

    # the array equality condition isn't right, because the missed calls don't have corresponding tnms
    if len(cnd_arr) > 0 and len(cnd_arr) == len(tnm_arr):
        return 'Joined'

    return 'Single'


def extract_ctype_and_duration(sarr):
    p = re.compile(' *'.join([ctype_exp, duration_exp]) + '$')
    cnd_arr = [x for x in sarr if bool(re.match(p, x.strip()))]

    if len(cnd_arr) > 0:
        res = []

        for cnd in cnd_arr:
            obj = {}
            [obj['ctype'], obj['duration']] = re.findall(p, cnd.strip())[0]
            res.append(obj)

    return res


def extract_time_and_memory(sarr):
    p = re.compile(' *'.join([time_exp, memory_exp]) + '$')
    tnm_arr = [x for x in sarr if bool(re.match((p, x.strip())))]

    if len(tnm_arr) > 0:
        res = []

        for tnm in tnm_arr:
            obj = {}
            [obj['time'], obj['memory']] = re.findall(p, tnm.strip())[0]
            res.append(obj)

    return res


def extract_date(sarr, msgno):
    p = re.compile(' *'.join([day_exp, month_exp, year_exp]) + '$')
    dates = [(i, x) for i, x in enumerate(sarr) if bool(re.match(p, x.strip()))]
    if len(dates) > 1:
        print('Found more than 1 date for msg no.{}'.format(msgno))

    # if date isn't represented in a way that matches expectations, it will throw here

    return dates[-1]


def parse_image_arr(sarr, i):
    # parses the array of string

    parsed = {}
    parsed['msgno'] = i
    parsed['raw'] = sarr
    parsed['name'] = extract_name(sarr)
    dl = extract_date(sarr, msgno=i)
    parsed['date'] = dl[1]
    parsed['calls'] = []
    parsed['unknown tokens'] =[]

    sarr = sarr[dl[0]+1:]  # only take the part of the array dealing with the calls info
    pt = ''
    for l in sarr:
        lt = get_line_type(l, pt)
        pt = lt

        if lt == 'cnd':
            [ctype, duration] = re.findall(patterns['pcnd'], l)[0]
            call = {}
            call['ctype'] = ctype
            call['duration'] = duration
            if duration == 'Not answered':
                call['size'] = 0
            parsed['calls'].append(call)
        elif lt == 'c':
            ctype = re.findall((patterns['pc']), l)[0]
            call = {}
            call['ctype'] = ctype
            if ctype == 'Missed':
                call['duration'] = 0
                call['size'] = 0
            parsed['calls'].append(call)
        elif lt == 'd':
            duration = re.findall(patterns['pd'], l)[0]
            call = next((c for c in parsed['calls'] if 'duration' not in c), {})
            # if len(call) == 0, throw('found duration token, but no where to place it')
            call['duration'] = duration
        elif lt == 'tnm':
            [timeh, timem, size] = re.findall(patterns['ptnm'], l)[0]
            call = next((c for c in parsed['calls'] if 'time' not in c and 'size' not in c), {})
            call['time'] = timeh+timem
            call['size'] = size
        elif lt == 't':
            [timeh, timem] = re.findall(patterns['pt'], l)[0]
            call = next((c for c in parsed['calls'] if 'time' not in c), {})
            call['time'] = timeh+timem
        elif lt == 'm':
            size = re.findall(patterns['pm'], l)[0]
            call = next((c for c in parsed['calls'] if 'size' not in c), {})
            call['size'] = size
        elif lt == 'u':
            parsed['unknown tokens'].append(l)

    # parsed['msgformat'] = get_format_type(sarr)
    # if parsed['msgformat'] == 'Joined':
    #     cnd = extract_ctype_and_duration(sarr)
    #     tnm = extract_time_and_memory(sarr)
    #     parsed['calls'] = [dict(a, **b) for (a, b) in zip(cnd, tnm)]

    return parsed


def img_to_arr(img):
    # converts an image of wa call log into an array of strings

    str_out = pytesseract.image_to_string(img)
    sarr = str_out.split('\n')
    p = re.compile("( *$|\\f)")
    sarr = [x for x in sarr if not bool(re.match(p, x))]

    return sarr

res = []
for i in range(1, 100):
    img = cv2.imread('/Users/Desktop/whatsapp call logs/snip_{}.png'.format(i))
    sarr = img_to_arr(img)
    try:
        parsed = parse_image_arr(sarr, i)
        res.append(parsed)
    except:
        print('!!!Error parsing image no.', i, '!!!')

parsing_failures = [x for x in res if len(x['unknown tokens']) >0]



