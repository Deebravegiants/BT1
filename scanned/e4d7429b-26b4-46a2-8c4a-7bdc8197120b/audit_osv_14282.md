# [H] CVE-2018-8789

## Summary
Severity: High
Advisory: CVE-2018-8789
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-8789
Type: osv

## Details
FreeRDP prior to version 2.0.0-rc4 contains several Out-Of-Bounds Reads in the NTLM Authentication module that results in a Denial of Service (segfault).

## References
- https://usn.ubuntu.com/3845-2/
- http://www.securityfocus.com/bid/106938
- https://lists.debian.org/debian-lts-announce/2019/02/msg00015.html
- https://usn.ubuntu.com/3845-1/
- https://github.com/FreeRDP/FreeRDP/commit/2ee663f39dc8dac3d9988e847db19b2d7e3ac8c6
- https://research.checkpoint.com/reverse-rdp-attack-code-execution-on-rdp-clients/
