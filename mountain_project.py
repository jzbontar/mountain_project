import urllib
import re
import pickle
import cgi
import os

# craig = ('trapps', '/v/the-trapps/105798818')
# craig = ('nears', '/v/the-near-trapps/108142181')
# craig = ('seneca', '/v/seneca-rocks/105861910')
# craig = ('nrg', '/v/the-new-river-gorge/105855991')
craig = ('rrg', '/v/red-river-gorge/105841134')

if not os.path.isfile('{}.pkl'.format(craig[0])):
    routes_html = {}
    queue = [craig[1]]
    for url in queue:
        html = urllib.urlopen('https://www.mountainproject.com' + url).read()
        title = re.search(r'''<meta property="og:title" content="(.*)" />''', html).group(1)
        print title

        if 'YDS:' in html:
            routes_html[title] = html
        else:
            links = re.findall(r'''href=.([-a-z0-9/]*).*id='leftnav''', html)
            queue.extend(links)
    pickle.dump(routes_html, open('{}.pkl'.format(craig[0]), 'w'))
routes_html = pickle.load(open('{}.pkl'.format(craig[0])))

routes = []
for name, html in routes_html.items():
    grade = re.search(r'YDS:</a>&nbsp;(.*)</span>', html).group(1)
    grade_pro = re.search(r'(\w*)</h3>&nbsp;', html).group(1).strip()
    grade_parsed = re.search('5.(\d+)', grade)
    if grade_parsed is None:
        continue
    grade_parsed = int(grade_parsed.group(1))

    url = re.search(r'<meta property="og:url" content="(.*)" />', html).group(1)
    average = float(re.search(r'<meta itemprop="average" content="(.*)" />', html).group(1))
    votes = int(re.search(r'<meta itemprop="votes" content="(\d+)" />', html).group(1))
    fa = re.search(r'<tr><td valign="top">FA:&nbsp;</td><td><!--MPTEXT-->(.*?)<!--MPTEXTEND--></td></tr>', html).group(1)
    fa = cgi.escape(fa)
    sector = re.search('\t<td><b>(.*?)</b></td>', html).group(1)
    routes.append(dict(name=name, grade=grade, grade_pro=grade_pro, grade_parsed=grade_parsed, average=average, 
                       votes=votes, fa=fa, url=url, sector=sector))

f = open('{}.html'.format(craig[0]), 'w')
f.write('<table>\n')
for i, route in enumerate(sorted(routes, key=lambda r: (-r['average'], -r['votes'])), start=1):
    f.write('<tr>\n')
    name = '<a href="{}">{}</a>'.format(route['url'], route['name'].strip())
    for txt in ('{} ({})'.format(route['average'], route['votes']), '{} {}'.format(route['grade'], route['grade_pro']), name, route['sector']):
        f.write('<td>{}</td>\n'.format(txt))
    f.write('</tr>\n')
f.write('</table>\n')
