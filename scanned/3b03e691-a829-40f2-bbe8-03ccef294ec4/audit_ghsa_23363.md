# [M] python-apt Does Not Check Hash Signature

## Summary
Severity: Medium
Advisory: GHSA-pj65-3pf6-c5q4
CVE: CVE-2019-15796
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pj65-3pf6-c5q4
Type: github-advisory

## Affected
- PyPI: `python-apt` — affected >=0 <0.8.3ubuntu7.5
- PyPI: `python-apt` — affected >=0.9.0 <0.9.3.5ubuntu3
- PyPI: `python-apt` — affected >=1.2.0 <1.6.5ubuntu0.1
- PyPI: `python-apt` — affected >=1.7.0 <1.9.0ubuntu1.2
- PyPI: `python-apt` — affected >=1.9.1 <1.9.5

## Details
Python-apt doesn't check if hashes are signed in `Version.fetch_binary()` and `Version.fetch_source()` of apt/package.py or in `_fetch_archives()` of apt/cache.py in version 1.9.3ubuntu2 and earlier. This allows downloads from unsigned repositories which shouldn't be allowed and has been fixed in verisions 1.9.5, 1.9.0ubuntu1.2, 1.6.5ubuntu0.1, 1.1.0~beta1ubuntu0.16.04.7, 0.9.3.5ubuntu3+esm2, and 0.8.3ubuntu7.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15796
- https://github.com/excid3/python-apt
- https://usn.ubuntu.com/4247-1
- https://usn.ubuntu.com/4247-3
