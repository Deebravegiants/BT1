# [C] CVE-2015-9059

## Summary
Severity: Critical
Advisory: CVE-2015-9059
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-28
Source: https://osv.dev/vulnerability/CVE-2015-9059
Type: osv

## Details
picocom before 2.0 has a command injection vulnerability in the 'send and receive file' command because the command line is executed by /bin/sh unsafely.

## References
- https://github.com/npat-efault/picocom/commit/1ebc60b20fbe9a02436d5cbbf8951714e749ddb1
- https://github.com/npat-efault/picocom/commit/1ebc60b20fbe9a02436d5cbbf8951714e749ddb1
- https://lists.debian.org/debian-lts-announce/2020/06/msg00030.html
