# [H] Open Redirect in httpie

## Summary
Severity: High
Advisory: GHSA-xjjg-vmw6-c2p9
CVE: CVE-2019-10751
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-08-27
Source: https://github.com/advisories/GHSA-xjjg-vmw6-c2p9
Type: github-advisory

## Affected
- PyPI: `httpie` — affected >=0 <1.0.3

## Details
All versions of the HTTPie package prior to version 1.0.3 are vulnerable to Open Redirect that allows an attacker to write an arbitrary file with supplied filename and content to the current directory, by redirecting a request from HTTP to a crafted URL pointing to a server in his or hers control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10751
- https://github.com/advisories/GHSA-xjjg-vmw6-c2p9
- https://github.com/jakubroztocil/httpie
- https://github.com/jakubroztocil/httpie/releases/tag/1.0.3
- https://github.com/pypa/advisory-database/tree/main/vulns/httpie/PYSEC-2019-23.yaml
- https://lists.debian.org/debian-lts-announce/2019/09/msg00031.html
- https://snyk.io/vuln/SNYK-PYTHON-HTTPIE-460107
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00022.html
