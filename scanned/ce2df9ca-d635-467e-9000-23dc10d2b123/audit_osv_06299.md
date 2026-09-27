# [C] BIT-libpython-2022-48565

## Summary
Severity: Critical
Advisory: BIT-libpython-2022-48565
Aliases: BIT-python-2022-48565, BIT-python-min-2022-48565, CVE-2022-48565, GHSA-crhm-wc96-7579, PSF-2023-5
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2022-48565
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.1

## Details
An XML External Entity (XXE) issue was discovered in Python through 3.9.1. The plistlib module no longer accepts entity declarations in XML plist files to avoid XML vulnerabilities.

## References
- https://bugs.python.org/issue42051
- https://lists.debian.org/debian-lts-announce/2023/09/msg00022.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AFHYAGWBFBNUGWU6XWKBHTCV5NH77MB7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BAYWJD576JUKLHCWKDLMJSUGTRDKPF3M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KZRZRJHWLZ7MOJNPQBWGJVXMVYDC5BRA/
- https://nvd.nist.gov/vuln/detail/CVE-2022-48565
- https://security.netapp.com/advisory/ntap-20231006-0007/
