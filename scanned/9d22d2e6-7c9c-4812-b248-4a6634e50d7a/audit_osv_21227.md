# [M] CVE-2021-41229

## Summary
Severity: Medium
Advisory: CVE-2021-41229
Aliases: GHSA-3fqg-r8j5-f5xq
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-12
Source: https://osv.dev/vulnerability/CVE-2021-41229
Type: osv

## Details
BlueZ is a Bluetooth protocol stack for Linux. In affected versions a vulnerability exists in sdp_cstate_alloc_buf which allocates memory which will always be hung in the singly linked list of cstates and will not be freed. This will cause a memory leak over time. The data can be a very large object, which can be caused by an attacker continuously sending sdp packets and this may cause the service of the target device to crash.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00022.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00022.html
- https://lists.debian.org/debian-lts-announce/2022/10/msg00026.html
- https://security.netapp.com/advisory/ntap-20211203-0004/
- https://github.com/bluez/bluez/security/advisories/GHSA-3fqg-r8j5-f5xq
