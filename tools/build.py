"""THM 코리아 사이트 빌드.

index.src.html(한국어 원본)에서
  1) 호환 표(크랭크, 핸들바)를 채워 index.html(한국어)을 만들고
  2) i18n/en.json, i18n/ja.json 번역으로 en/index.html, ja/index.html을 만들고
  3) sitemap.xml을 다시 씁니다.

사용법: python3 tools/build.py
문구를 고친 뒤에는 python3 i18n/extract.py 로 ko.json을 갱신하고,
새로 생긴 문장만 en.json / ja.json에 추가한 다음 빌드합니다.
"""
import json, re, sys, pathlib, datetime
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'i18n'))
from extract import HANGUL  # noqa: E402

SITE = 'https://thm.rubiworkshop.com/'

# ---------------------------------------------------------------- fit tables
# THM 공식 기술 정보(thm.bike, 2026-10 기준). 무게는 ±5%.
CRANKS = [
  # 모델, 용도, 무게, 체인링 인터페이스, 축, Q 팩터, 체인라인, 크랭크 길이
  ('Clavicula SE Compact', '로드', '293g', '5볼트 BCD 110', '카본 30mm', '151mm', '45mm', '160 ~ 175mm'),
  ('Clavicula SE Standard', '로드', '302g', '5볼트 BCD 130', '카본 30mm', '151mm', '45mm', '160 ~ 175mm'),
  ('Clavicula SE 파워미터', '로드', '320g / 329g', '5볼트 BCD 110 / 130', '카본 30mm (센서 내장)', '151mm', '45mm', '루비워크샵 문의'),
  ('Clavicula DM', '로드', '255g', '8볼트 다이렉트 마운트', '카본 29mm (DUB)', '148mm', '45mm', '165 ~ 172.5mm'),
  ('Clavicula XC', 'MTB', '299g', '4볼트 BCD 104', '카본', '168mm', '52mm (부스트)', '170 ~ 175mm'),
]
BARS = [
  # 모델, 무게, 폭(C-C), 드롭, 리치, 플레어, 스템 길이, 스택
  ('Ulna', '155g (42cm)', '40 / 42 / 44cm', '119mm', '77mm', '6°', '별도 스템', '-'),
  ('Frontale', '222g (420 x 100)', '40 / 42 / 44cm', '119mm', '77mm', '6°', '90 / 100 / 110mm, -6°', '40mm'),
  ('Frontale Aero', '250g 이하 (420 x 100)', '38 / 40 / 42cm', '127mm', '75mm', '7°', '100 / 110 / 120mm, -6°', '38mm'),
]

def table(head, rows):
    h = '<table class="size fit"><thead><tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr></thead><tbody>'
    for r in rows:
        h += f'<tr><th>{r[0]}</th>' + ''.join(f'<td>{v}</td>' for v in r[1:]) + '</tr>'
    return h + '</tbody></table>'

def crank_table():
    return table(['모델', '용도', '무게', '체인링', '축', 'Q 팩터', '체인라인', '크랭크 길이'], CRANKS)

def bar_table():
    return table(['모델', '무게', '폭', '드롭', '리치', '플레어', '스템', '스택'], BARS)

def build_ko():
    s = (ROOT / 'index.src.html').read_text()
    s = s.replace('{{CRANK_TABLE}}', crank_table()).replace('{{BAR_TABLE}}', bar_table())
    assert '{{' not in s
    assert '—' not in re.sub(r'<!--.*?-->', '', s, flags=re.S), 'em dash in Korean page'
    (ROOT / 'index.html').write_text(s)
    return s

# ---------------------------------------------------------------- translate
LANG = {
 'en': {'locale': 'en_US', 'path': 'en/'},
 'ja': {'locale': 'ja_JP', 'path': 'ja/'},
}

def translate(ko_html, lang):
    tr = json.loads((ROOT / f'i18n/{lang}.json').read_text())
    missing = set()
    def t(s):
        k = s.strip()
        if not HANGUL.search(k):
            return s
        if k in tr:
            return s.replace(k, tr[k])
        missing.add(k)
        return s

    soup = BeautifulSoup(ko_html, 'html.parser')
    soup.html['lang'] = lang
    if soup.title:
        soup.title.string = t(soup.title.string)
    for m in soup.find_all('meta'):
        if m.has_attr('content'):
            m['content'] = t(m['content'])
    for sc in soup.find_all('script', type='application/ld+json'):
        data = json.loads(sc.string)
        def walk(o):
            if isinstance(o, dict):
                return {k: walk(v) for k, v in o.items()}
            if isinstance(o, list):
                return [walk(v) for v in o]
            if isinstance(o, str):
                return t(o)
            return o
        data = walk(data)
        for node in data.get('@graph', []):
            if node.get('@type') == 'WebSite':
                node['url'] = SITE + LANG[lang]['path']
                node['inLanguage'] = lang
        sc.string = '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    for el in soup.body.find_all(True):
        for a in ('alt', 'aria-label', 'title'):
            if el.has_attr(a):
                el[a] = t(el[a])

    def visit(el):
        if el.name in ('script', 'style'):
            return
        direct = any(isinstance(c, NavigableString) and not isinstance(c, Comment) and HANGUL.search(c) for c in el.children)
        if direct:
            k = el.decode_contents().strip()
            if k in tr:
                el.clear()
                frag = BeautifulSoup(tr[k], 'html.parser')
                for c in list(frag.contents):
                    el.append(c)
            else:
                missing.add(k)
            return
        for c in list(el.children):
            if getattr(c, 'name', None):
                visit(c)
    visit(soup.body)

    # canonical, og, hreflang self, language switcher
    soup.find('link', rel='canonical')['href'] = SITE + LANG[lang]['path']
    soup.find('meta', property='og:url')['content'] = SITE + LANG[lang]['path']
    soup.find('meta', property='og:locale')['content'] = LANG[lang]['locale']
    for a in soup.select('nav.lang a'):
        code = a['hreflang']
        a['href'] = '../' if code == 'ko' else ('./' if code == lang else f'../{code}/')
        if code == lang:
            a['class'] = ['on']; a['aria-current'] = 'page'
        else:
            a.attrs.pop('class', None); a.attrs.pop('aria-current', None)
    if lang == 'ja':
        # 일본어는 한글 서체(에스코어 드림) 대신 Noto Sans JP로 통일 (영문·숫자는 Pretendard 유지)
        style = soup.find('style')
        for tag in BeautifulSoup('<link rel="preconnect" href="https://fonts.googleapis.com">'
                                 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                                 '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400&display=swap" rel="stylesheet">'
                                 '<style>:root{--font:"RubiLatin","Noto Sans JP","Hiragino Sans","Yu Gothic",system-ui,sans-serif}</style>',
                                 'html.parser').contents[:]:
            style.insert_after(tag) if tag.name == 'style' else style.insert_before(tag)

    out = str(soup)
    # 하위 폴더에서 이미지 경로 보정
    out = out.replace('src="images/', 'src="../images/').replace('url(images/', 'url(../images/').replace('href="images/', 'href="../images/')
    left = [k for k in missing]
    return out, left

def sitemap(html):
    imgs = sorted(set(re.findall(r'images/[\w/.-]+\.(?:jpg|png|webp)', html)))
    imgs = [i for i in imgs if not re.search(r'logo|favicon|apple-touch', i)]
    today = datetime.date.today().isoformat()
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{SITE}{p}"/>' for h, p in [('ko', ''), ('en', 'en/'), ('ja', 'ja/'), ('x-default', '')])
    urls = []
    for p in ['', 'en/', 'ja/']:
        u = f'  <url>\n    <loc>{SITE}{p}</loc>{alts}\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{"1.0" if not p else "0.8"}</priority>'
        if not p:
            u += ''.join(f'\n    <image:image><image:loc>{SITE}{i}</image:loc></image:image>' for i in imgs)
        urls.append(u + '\n  </url>')
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
         'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
         + '\n'.join(urls) + '\n</urlset>\n')
    (ROOT / 'sitemap.xml').write_text(x)

if __name__ == '__main__':
    ko = build_ko()
    print('ko  index.html', len(ko))
    for lang in LANG:
        if not (ROOT / f'i18n/{lang}.json').exists():
            print(lang, 'skipped (no translation file)'); continue
        out, left = translate(ko, lang)
        d = ROOT / LANG[lang]['path']; d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(out)
        hangul = len(HANGUL.findall(re.sub(r'<script(?![^>]*ld\+json).*?</script>', '', out, flags=re.S)))
        print(lang, f'{d.name}/index.html', len(out), 'untranslated units:', len(left), 'hangul chars left:', hangul)
        for k in left[:20]:
            print('   -', k[:90])
    sitemap(ko)
