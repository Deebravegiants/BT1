# [M] BIT-libpython-2022-48566

## Summary
Severity: Medium
Advisory: BIT-libpython-2022-48566
Aliases: BIT-python-2022-48566, BIT-python-min-2022-48566, CVE-2022-48566, GHSA-cgfh-jp5w-8cmx, PSF-2023-6
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2022-48566
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.1

## Details
An issue was discovered in compare_digest in Lib/hmac.py in Python through 3.9.1. Constant-time-defeating optimisations were possible in the accumulator variable in hmac.compare_digest.

## References
- https://bugs.python.org/issue40791
- https://lists.debian.org/debian-lts-announce/2023/09/msg00022.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00017.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-48566
- https://security.netapp.com/advisory/ntap-20231006-0013/
