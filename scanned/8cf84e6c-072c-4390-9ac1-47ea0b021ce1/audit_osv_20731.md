# [M] CVE-2021-3652

## Summary
Severity: Medium
Advisory: CVE-2021-3652
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2021-3652
Type: osv

## Details
A flaw was found in 389-ds-base. If an asterisk is imported as password hashes, either accidentally or maliciously, then instead of being inactive, any password will successfully match during authentication. This flaw allows an attacker to successfully authenticate as a user whose password was disabled.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00026.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00015.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1982782
- https://github.com/389ds/389-ds-base/issues/4817
