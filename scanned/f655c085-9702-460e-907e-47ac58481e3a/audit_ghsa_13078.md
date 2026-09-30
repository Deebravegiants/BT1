# [M] Authenticated Local Privilege Escalation vulnerability in Intel Optimization for Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-m2f8-v8q4-3m59
CVE: CVE-2023-27506
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-m2f8-v8q4-3m59
Type: github-advisory

## Affected
- PyPI: `intel-tensorflow` — affected >=0 <2.12
- PyPI: `tensorflow-intel` — affected >=0 <2.12
- PyPI: `intel-tensorflow-avx512` — affected >=0 <2.12

## Details
Improper buffer restrictions in the Intel(R) Optimization for Tensorflow software before version 2.12 may allow an authenticated user to potentially enable escalation of privilege via local access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27506
- http://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00840.html
