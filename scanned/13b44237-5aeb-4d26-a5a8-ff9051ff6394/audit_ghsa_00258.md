# [M] feedparser Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2p78-8hh6-96xc
CVE: CVE-2011-1157
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-2p78-8hh6-96xc
Type: github-advisory

## Affected
- PyPI: `feedparser` — affected >=5.0 <5.0.1

## Details
Cross-site scripting (XSS) vulnerability in feedparser.py in Universal Feed Parser (aka feedparser or python-feedparser) 5.x before 5.0.1 allows remote attackers to inject arbitrary web script or HTML via malformed XML comments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1157
- https://bugzilla.novell.com/show_bug.cgi?id=680074
- https://bugzilla.redhat.com/show_bug.cgi?id=684877
- https://code.google.com/p/feedparser/issues/detail?id=254
- https://github.com/advisories/GHSA-2p78-8hh6-96xc
- https://github.com/kurtmckee/feedparser
- https://github.com/pypa/advisory-database/tree/main/vulns/feedparser/PYSEC-2011-20.yaml
- https://web.archive.org/web/20210121212051/https://www.securityfocus.com/bid/46867
- https://web.archive.org/web/20240723030532/https://tuxedo.org/mandriva/?name=MDVSA-2011:082
- http://lists.opensuse.org/opensuse-updates/2011-04/msg00026.html
- http://openwall.com/lists/oss-security/2011/03/14/18
- http://openwall.com/lists/oss-security/2011/03/15/11
- http://support.novell.com/security/cve/CVE-2011-1157.html
