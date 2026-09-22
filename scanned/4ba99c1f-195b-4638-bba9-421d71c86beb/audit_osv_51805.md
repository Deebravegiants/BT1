# [H] CVE-2021-4091

## Summary
Severity: High
Advisory: CVE-2021-4091
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-4091
Type: osv

## Details
A double-free was found in the way 389-ds-base handles virtual attributes context in persistent searches. An attacker could send a series of search requests, forcing the server to behave unexpectedly, and crash.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00026.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00015.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2030307
