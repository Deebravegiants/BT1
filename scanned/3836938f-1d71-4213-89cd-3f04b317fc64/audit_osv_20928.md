# [H] CVE-2021-38576

## Summary
Severity: High
Advisory: CVE-2021-38576
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-03
Source: https://osv.dev/vulnerability/CVE-2021-38576
Type: osv

## Details
A BIOS bug in firmware for a particular PC model leaves the Platform authorization value empty. This can be used to permanently brick the TPM in multiple ways, as well as to non-permanently DoS the system.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00007.html
- https://bugzilla.tianocore.org/show_bug.cgi?id=3499
