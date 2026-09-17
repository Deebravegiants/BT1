# [C] pysaml2 Improper Authentication vulnerability

## Summary
Severity: Critical
Advisory: GHSA-924m-4pmx-c67h
CVE: CVE-2017-1000433
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-924m-4pmx-c67h
Type: github-advisory

## Affected
- PyPI: `pysaml2` — affected >=0 <4.5.0

## Details
pysaml2 version 4.4.0 and older accept any password when run with python optimizations enabled. This allows attackers to log in as any user without knowing their password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000433
- https://github.com/rohe/pysaml2/issues/451
- https://github.com/IdentityPython/pysaml2/pull/454
- https://github.com/IdentityPython/pysaml2/commit/6312a41e037954850867f29d329e5007df1424a5
- https://github.com/advisories/GHSA-924m-4pmx-c67h
- https://github.com/pypa/advisory-database/tree/main/vulns/pysaml2/PYSEC-2018-48.yaml
- https://github.com/rohe/pysaml2
- https://lists.debian.org/debian-lts-announce/2018/07/msg00000.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00038.html
- https://security.gentoo.org/glsa/201801-11
