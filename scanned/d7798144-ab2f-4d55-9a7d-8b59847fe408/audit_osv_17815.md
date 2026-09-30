# [C] CVE-2020-20276

## Summary
Severity: Critical
Advisory: CVE-2020-20276
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-18
Source: https://osv.dev/vulnerability/CVE-2020-20276
Type: osv

## Details
An unauthenticated stack-based buffer overflow vulnerability in common.c's handle_PORT in uftpd FTP server versions 2.10 and earlier can be abused to cause a crash and could potentially lead to remote code execution.

## References
- https://arinerron.com/blog/posts/6
- https://github.com/troglobit/uftpd/commit/0fb2c031ce0ace07cc19cd2cb2143c4b5a63c9dd
