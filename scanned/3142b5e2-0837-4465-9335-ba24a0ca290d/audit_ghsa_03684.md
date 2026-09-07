# [H] Code Injection in PyXDG

## Summary
Severity: High
Advisory: GHSA-r6v3-hpxj-r8rv
CVE: CVE-2019-12761
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-06-07
Source: https://github.com/advisories/GHSA-r6v3-hpxj-r8rv
Type: github-advisory

## Affected
- PyPI: `pyxdg` — affected >=0 <0.26

## Details
A code injection issue was discovered in PyXDG before 0.26 via crafted Python code in a Category element of a Menu XML document in a .menu file. XDG_CONFIG_DIRS must be set up to trigger xdg.Menu.parse parsing within the directory containing this file. This is due to a lack of sanitization in xdg/Menu.py before an eval call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12761
- https://gist.github.com/dhondta/b45cd41f4186110a354dc7272916feba
- https://github.com/pypa/advisory-database/tree/main/vulns/pyxdg/PYSEC-2019-199.yaml
- https://github.com/takluyver/pyxdg
- https://lists.debian.org/debian-lts-announce/2019/06/msg00006.html
- https://lists.debian.org/debian-lts-announce/2021/08/msg00003.html
- https://snyk.io/vuln/SNYK-PYTHON-PYXDG-174562
