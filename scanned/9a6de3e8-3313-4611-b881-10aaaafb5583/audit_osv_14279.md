# [C] CVE-2018-8786

## Summary
Severity: Critical
Advisory: CVE-2018-8786
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-8786
Type: osv

## Details
FreeRDP prior to version 2.0.0-rc4 contains an Integer Truncation that leads to a Heap-Based Buffer Overflow in function update_read_bitmap_update() and results in a memory corruption and probably even a remote code execution.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YVJKO2DR5EY4C4QZOP7SNNBEW2JW6FHX/
- http://www.securityfocus.com/bid/106938
- https://access.redhat.com/errata/RHSA-2019:0697
- https://lists.debian.org/debian-lts-announce/2019/02/msg00015.html
- https://usn.ubuntu.com/3845-1/
- https://usn.ubuntu.com/3845-2/
- https://github.com/FreeRDP/FreeRDP/commit/445a5a42c500ceb80f8fa7f2c11f3682538033f3
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
