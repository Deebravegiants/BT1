# [H] PyPXE Buffer Overflow vulnerability

## Summary
Severity: High
Advisory: GHSA-82wx-rxf8-fxch
CVE: CVE-2023-46960
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-04-29
Source: https://github.com/advisories/GHSA-82wx-rxf8-fxch
Type: github-advisory

## Affected
- PyPI: `PyPXE` — affected >=0

## Details
Buffer Overflow vulnerability in PyPXE v.1.8.4 allows a remote attacker to cause a denial of service via the handle function in the tftp module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46960
- https://github.com/pypxe/PyPXE/issues/206
- https://github.com/pypxe/PyPXE
