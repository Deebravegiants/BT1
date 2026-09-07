# [M] Improper Neutralization of Input During Web Page Generation in IPython

## Summary
Severity: Medium
Advisory: GHSA-66gw-5xpf-gfp5
CVE: CVE-2015-4707
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-66gw-5xpf-gfp5
Type: github-advisory

## Affected
- PyPI: `ipython` — affected >=0 <3.2.0

## Details
Cross-site scripting (XSS) vulnerability in IPython before 3.2 allows remote attackers to inject arbitrary web script or HTML via vectors involving JSON error messages and the /api/notebooks path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-4707
- https://github.com/ipython/ipython/commit/7222bd53ad089a65fd610fab4626f9d0ab47dfce
- https://github.com/ipython/ipython/commit/c2078a53543ed502efd968649fee1125e0eb549c
- https://bugzilla.redhat.com/show_bug.cgi?id=1235688
- https://github.com/advisories/GHSA-66gw-5xpf-gfp5
- https://github.com/ipython/ipython
- https://github.com/pypa/advisory-database/tree/main/vulns/ipython/PYSEC-2017-46.yaml
- https://ipython.org/ipython-doc/3/whatsnew/version3.html
- https://web.archive.org/web/20200227150022/https://www.securityfocus.com/bid/75328
- http://www.openwall.com/lists/oss-security/2015/06/22/7
