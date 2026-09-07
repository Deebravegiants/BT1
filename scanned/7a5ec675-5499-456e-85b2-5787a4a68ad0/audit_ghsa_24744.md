# [M] lxml Cross-site Scripting Via Control Characters

## Summary
Severity: Medium
Advisory: GHSA-57qw-cc2g-pv5p
CVE: CVE-2014-3146
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-57qw-cc2g-pv5p
Type: github-advisory

## Affected
- PyPI: `lxml` — affected >=0 <3.3.5

## Details
Incomplete blacklist vulnerability in the `lxml.html.clean` module in lxml before 3.3.5 allows remote attackers to conduct cross-site scripting (XSS) attacks via control characters in the link scheme to the `clean_html` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3146
- https://github.com/lxml/lxml/pull/273
- https://github.com/lxml/lxml/commit/3f3082e0a67851cde26a48da3d1f4b75d8aa07ec
- https://github.com/lxml/lxml/commit/86e81ab393ba14c1be71284675851a3bdce57d69
- https://github.com/lxml/lxml/commit/e86b294f1f81b899a59925123560ff924a72f1cc
- https://github.com/lxml/lxml
- https://github.com/pypa/advisory-database/tree/main/vulns/lxml/PYSEC-2014-9.yaml
- https://mailman-mail5.webfaction.com/pipermail/lxml/2014-April/007128.html
- https://web.archive.org/web/20140724172044/http://secunia.com/advisories/58013
- https://web.archive.org/web/20140805110535/http://secunia.com/advisories/59008
- https://web.archive.org/web/20140806061046/http://secunia.com/advisories/58744
- https://web.archive.org/web/20141017122607/https://mailman-mail5.webfaction.com/pipermail/lxml/2014-April/007128.html
- https://web.archive.org/web/20150523055039/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2015:112/?name=MDVSA-2015:112
- https://web.archive.org/web/20200228180542/http://www.securityfocus.com/bid/67159
- http://advisories.mageia.org/MGASA-2014-0218.html
- http://lists.opensuse.org/opensuse-updates/2014-05/msg00083.html
- http://lxml.de/3.3/changes-3.3.5.html
- http://seclists.org/fulldisclosure/2014/Apr/210
- http://seclists.org/fulldisclosure/2014/Apr/319
- http://www.debian.org/security/2014/dsa-2941
