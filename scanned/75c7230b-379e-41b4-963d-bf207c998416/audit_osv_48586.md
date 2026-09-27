# [M] CVE-2017-9832

## Summary
Severity: Medium
Advisory: CVE-2017-9832
CVSS: 6.8 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-24
Source: https://osv.dev/vulnerability/CVE-2017-9832
Type: osv

## Details
An integer overflow vulnerability in ptp-pack.c (ptp_unpack_OPL function) of libmtp (version 1.1.12 and below) allows attackers to cause a denial of service (out-of-bounds memory access) or maybe remote code execution by inserting a mobile device into a personal computer through a USB cable.

## References
- https://lists.debian.org/debian-lts-announce/2020/04/msg00003.html
- https://sourceforge.net/p/libmtp/mailman/message/35729062
