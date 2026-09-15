# [M] BIT-libpython-2022-48564

## Summary
Severity: Medium
Advisory: BIT-libpython-2022-48564
Aliases: BIT-python-2022-48564, BIT-python-min-2022-48564, CVE-2022-48564, GHSA-p8vw-m6qq-w42v, PSF-2023-10
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2022-48564
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.1

## Details
read_ints in plistlib.py in Python through 3.9.1 is vulnerable to a potential DoS attack via CPU and RAM exhaustion when processing malformed Apple Property List files in binary format.

## References
- https://bugs.python.org/issue42103
- https://lists.debian.org/debian-lts-announce/2023/10/msg00017.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-48564
- https://security.netapp.com/advisory/ntap-20230929-0009/
