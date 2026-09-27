# [H] Directory Traversal in Babel

## Summary
Severity: High
Advisory: GHSA-h4m5-qpfp-3mpv
CVE: CVE-2021-42771
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-21
Source: https://github.com/advisories/GHSA-h4m5-qpfp-3mpv
Type: github-advisory

## Affected
- PyPI: `babel` — affected >=0 <2.9.1

## Details
Babel.Locale in Babel before 2.9.1 allows attackers to load arbitrary locale .dat files (containing serialized Python objects) via directory traversal, leading to code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42771
- https://github.com/python-babel/babel/pull/782
- https://github.com/python-babel/babel/commit/412015ef642bfcc0d8ba8f4d05cdbb6aac98d9b3
- https://github.com/advisories/GHSA-h4m5-qpfp-3mpv
- https://github.com/pypa/advisory-database/tree/main/vulns/babel/PYSEC-2021-421.yaml
- https://github.com/python-babel/babel
- https://lists.debian.org/debian-lts-announce/2021/10/msg00018.html
- https://lists.debian.org/debian-lts/2021/10/msg00040.html
- https://www.debian.org/security/2021/dsa-5018
- https://www.tenable.com/security/research/tra-2021-14
