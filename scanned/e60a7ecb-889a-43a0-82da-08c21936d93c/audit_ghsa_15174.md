# [H] PyCryptodome and pycryptodomex side-channel leakage for OAEP decryption

## Summary
Severity: High
Advisory: GHSA-j225-cvw7-qrx7
CVE: CVE-2023-52323
CWE: CWE-203
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-05
Source: https://github.com/advisories/GHSA-j225-cvw7-qrx7
Type: github-advisory

## Affected
- PyPI: `pycryptodomex` — affected >=0 <3.19.1
- PyPI: `pycryptodome` — affected >=0 <3.19.1

## Details
PyCryptodome and pycryptodomex before 3.19.1 allow side-channel leakage for OAEP decryption, exploitable for a Manger attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52323
- https://github.com/Legrandin/pycryptodome/commit/0deea1bfe1489e8c80d2053bbb06a1aa0b181ebd
- https://github.com/Legrandin/pycryptodome
- https://github.com/Legrandin/pycryptodome/blob/master/Changelog.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/pycryptodomex/PYSEC-2024-3.yaml
- https://pypi.org/project/pycryptodomex/#history
