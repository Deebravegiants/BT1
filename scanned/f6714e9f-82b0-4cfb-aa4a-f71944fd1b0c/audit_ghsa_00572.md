# [C] python-gnupg vulnerable to shell injection

## Summary
Severity: Critical
Advisory: GHSA-vcr5-xr9h-mvc5
CVE: CVE-2014-1929
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-vcr5-xr9h-mvc5
Type: github-advisory

## Affected
- PyPI: `python-gnupg` — affected >=0.3.5 <0.3.7

## Details
python-gnupg 0.3.5 and 0.3.6 allow for shell injection via a failure to escape backslashes in the `shell_quote()` function. NOTE: this vulnerability exists because of an incomplete fix for CVE-2013-7323.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1929
- https://alioth-lists.debian.net/pipermail/debian-security-tracker-commits/2014-June/028512.html
- https://code.google.com/archive/p/python-gnupg/issues/98
- https://github.com/advisories/GHSA-vcr5-xr9h-mvc5
- https://github.com/pypa/advisory-database/tree/main/vulns/python-gnupg/PYSEC-2014-92.yaml
- https://github.com/vsajip/python-gnupg
- https://web.archive.org/web/20200228170437/http://www.securityfocus.com/bid/65539
- https://www.openwall.com/lists/oss-security/2014/02/04/3
- https://www.openwall.com/lists/oss-security/2014/02/04/4
- http://seclists.org/oss-sec/2014/q1/245
- http://seclists.org/oss-sec/2014/q1/335
- http://www.debian.org/security/2014/dsa-2946
