# [C] CVE-2018-8788

## Summary
Severity: Critical
Advisory: CVE-2018-8788
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-8788
Type: osv

## Details
FreeRDP prior to version 2.0.0-rc4 contains an Out-Of-Bounds Write of up to 4 bytes in function nsc_rle_decode() that results in a memory corruption and possibly even a remote code execution.

## References
- https://usn.ubuntu.com/3845-2/
- http://www.securityfocus.com/bid/106938
- https://access.redhat.com/errata/RHSA-2019:0697
- https://lists.debian.org/debian-lts-announce/2019/02/msg00015.html
- https://usn.ubuntu.com/3845-1/
- https://github.com/FreeRDP/FreeRDP/commit/d1112c279bd1a327e8e4d0b5f371458bf2579659
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
