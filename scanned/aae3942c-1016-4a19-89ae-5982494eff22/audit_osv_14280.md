# [C] CVE-2018-8787

## Summary
Severity: Critical
Advisory: CVE-2018-8787
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-8787
Type: osv

## Details
FreeRDP prior to version 2.0.0-rc4 contains an Integer Overflow that leads to a Heap-Based Buffer Overflow in function gdi_Bitmap_Decompress() and results in a memory corruption and probably even a remote code execution.

## References
- http://www.securityfocus.com/bid/106938
- https://access.redhat.com/errata/RHSA-2019:0697
- https://lists.debian.org/debian-lts-announce/2019/02/msg00015.html
- https://usn.ubuntu.com/3845-1/
- https://usn.ubuntu.com/3845-2/
- https://github.com/FreeRDP/FreeRDP/commit/09b9d4f1994a674c4ec85b4947aa656eda1aed8a
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
