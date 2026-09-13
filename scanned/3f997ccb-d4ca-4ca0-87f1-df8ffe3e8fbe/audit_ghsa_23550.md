# [H] Py2Play Unpickles Untrusted Objects

## Summary
Severity: High
Advisory: GHSA-wcpc-f63g-x26q
CVE: CVE-2005-2875
CWE: CWE-502
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-wcpc-f63g-x26q
Type: github-advisory

## Affected
- PyPI: `Py2Play` — affected >=0

## Details
Py2Play allows remote attackers to execute arbitrary Python code via pickled objects, which Py2Play unpickles and executes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2005-2875
- https://bugs.gentoo.org/show_bug.cgi?id=103524
- https://web.archive.org/web/20040824010038/http://home.gna.org/oomadness/fr/slune/index.html
- https://web.archive.org/web/20050213041706/http://soya.literati.org
- https://web.archive.org/web/20161225000907/http://www.securityfocus.com/bid/14864
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=326976
- http://www.debian.org/security/2005/dsa-856
- http://www.gentoo.org/security/en/glsa/glsa-200509-09.xml
