# [H] ALPINE-CVE-2018-19935

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-19935
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19935
Type: osv

## Affected
- Alpine:v3.5: `php5` — affected >=0 <5.6.39-r0

## Details
ext/imap/php_imap.c in PHP 5.x and 7.x before 7.3.0 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via an empty string in the message argument to the imap_mail function.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19935
