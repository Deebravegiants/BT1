# [M] CVE-2016-7440

## Summary
Severity: Medium
Advisory: CVE-2016-7440
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7440
Type: osv

## Details
The C software implementation of AES Encryption and Decryption in wolfSSL (formerly CyaSSL) before 3.9.10 makes it easier for local users to discover AES keys by leveraging cache-bank timing differences.

## References
- http://www.debian.org/security/2016/dsa-3706
- http://www.securityfocus.com/bid/93659
- http://www.securitytracker.com/id/1037050
- https://mariadb.com/kb/en/mariadb/mariadb-10028-release-notes/
- https://wolfssl.com/wolfSSL/Blog/Entries/2016/9/26_wolfSSL_3.9.10_Vulnerability_Fixes.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
