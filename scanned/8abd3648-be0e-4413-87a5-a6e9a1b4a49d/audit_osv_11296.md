# [M] CVE-2017-7274

## Summary
Severity: Medium
Advisory: CVE-2017-7274
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-7274
Type: osv

## Details
The r_pkcs7_parse_cms function in libr/util/r_pkcs7.c in radare2 1.3.0 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted PE file.

## References
- http://www.securityfocus.com/bid/97181
- https://github.com/radare/radare2/commit/7ab66cca5bbdf6cb2d69339ef4f513d95e532dbf
- https://github.com/radare/radare2/issues/7152
