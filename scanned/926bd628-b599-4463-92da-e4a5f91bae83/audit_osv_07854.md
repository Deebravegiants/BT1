# [C] FTP Server Response Buffer Overflow

## Summary
Severity: Critical
Advisory: CURL-CVE-2000-0973
Aliases: CVE-2000-0973
Published: 2000-10-13
Source: https://osv.dev/vulnerability/CURL-CVE-2000-0973
Type: osv

## Details
When storing an FTP server's error message on failure, there was no check for
input length and thus a malicious FTP server could overflow curl's stack based
buffer.
