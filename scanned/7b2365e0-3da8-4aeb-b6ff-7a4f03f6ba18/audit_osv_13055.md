# [H] CVE-2018-17106

## Summary
Severity: High
Advisory: CVE-2018-17106
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-16
Source: https://osv.dev/vulnerability/CVE-2018-17106
Type: osv

## Details
In Tinyftp Tinyftpd 1.1, a buffer overflow exists in the text variable of the do_mkd function in the ftpproto.c file. An attacker can overwrite ebp via a long pathname.

## References
- https://github.com/vbirds/Tinyftp/issues/4
