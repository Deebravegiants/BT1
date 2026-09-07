# [M] Paste is vulnerable to Cross-site Scripting via vectors involving a 404 status code

## Summary
Severity: Medium
Advisory: GHSA-7gfc-2v6g-6w9f
CVE: CVE-2010-2477
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7gfc-2v6g-6w9f
Type: github-advisory

## Affected
- PyPI: `paste` — affected >=0 <1.7.4

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the paste.httpexceptions implementation in Paste before 1.7.4 allow remote attackers to inject arbitrary web script or HTML via vectors involving a 404 status code, related to (1) paste.urlparser.StaticURLParser, (2) paste.urlparser.PkgResourcesParser, (3) paste.urlmap.URLMap, and (4) HTTPNotFound.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2477
- https://github.com/cdent/paste/commit/4910493c62f369a3222357af09450930e4c93f5e
- https://github.com/cdent/paste
- https://github.com/pypa/advisory-database/tree/main/vulns/paste/PYSEC-2010-29.yaml
- https://web.archive.org/web/20111227133546/http://secunia.com/advisories/42500
- https://web.archive.org/web/20120527154041/http://www.securityfocus.com/bid/41160
- http://bitbucket.org/ianb/paste/changeset/fcae59df8b56
- http://groups.google.com/group/paste-users/browse_thread/thread/3b3fff3dadd0b1e5?pli=1
- http://groups.google.com/group/pylons-discuss/msg/8c256dc076a408d8?dmode=source&output=gplain
- http://marc.info/?l=oss-security&m=127785414818815&w=2
- http://marc.info/?l=oss-security&m=127792576822169&w=2
- http://pylonshq.com/articles/archives/2010/6/paste_174_released_addresses_xss_security_hole
- http://www.ubuntu.com/usn/USN-1026-1
