# [H] CVE-2018-14363

## Summary
Severity: High
Advisory: CVE-2018-14363
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14363
Type: osv

## Details
An issue was discovered in NeoMutt before 2018-07-16. newsrc.c does not properly restrict '/' characters that may have unsafe interaction with cache pathnames.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00001.html
- https://neomutt.org/2018/07/16/release
- https://www.debian.org/security/2018/dsa-4277
- https://github.com/neomutt/neomutt/commit/9bfab35522301794483f8f9ed60820bdec9be59e
