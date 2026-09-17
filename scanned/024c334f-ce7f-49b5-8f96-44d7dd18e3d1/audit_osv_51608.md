# [M] CVE-2021-3514

## Summary
Severity: Medium
Advisory: CVE-2021-3514
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2021-3514
Type: osv

## Details
When using a sync_repl client in 389-ds-base, an authenticated attacker can cause a NULL pointer dereference using a specially crafted query, causing a crash.

## References
- https://github.com/389ds/389-ds-base/issues/4711
- https://lists.debian.org/debian-lts-announce/2023/04/msg00026.html
