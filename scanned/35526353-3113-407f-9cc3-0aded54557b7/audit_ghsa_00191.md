# [H] feedparser denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-hjf3-r7gw-9rwg
CVE: CVE-2012-2921
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-hjf3-r7gw-9rwg
Type: github-advisory

## Affected
- PyPI: `feedparser` — affected >=0 <5.1.2

## Details
Universal Feed Parser (aka feedparser or python-feedparser) before 5.1.2 allows remote attackers to cause a denial of service (memory consumption) via a crafted XML ENTITY declaration in a non-ASCII encoded document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2921
- https://code.google.com/p/feedparser/source/browse/trunk/NEWS?spec=svn706&r=706
- https://code.google.com/p/feedparser/source/detail?r=703&path=/trunk/feedparser/feedparser.py
- https://github.com/advisories/GHSA-hjf3-r7gw-9rwg
- https://github.com/kurtmckee/feedparser
- https://github.com/pypa/advisory-database/tree/main/vulns/feedparser/PYSEC-2012-14.yaml
- https://web.archive.org/web/20120604210617/http://www.securityfocus.com/bid/53654
- https://web.archive.org/web/20150523060531/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2013:118/?name=MDVSA-2013:118
- https://wiki.mageia.org/en/Support/Advisories/MGASA-2012-0157
- http://freecode.com/projects/feedparser/releases/344371
