# [H] CVE-2021-43766

## Summary
Severity: High
Advisory: CVE-2021-43766
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-43766
Type: osv

## Details
Odyssey passes to server unencrypted bytes from man-in-the-middle When Odyssey is configured to use certificate Common Name for client authentication, a man-in-the-middle attacker can inject arbitrary SQL queries when a connection is first established, despite the use of SSL certificate verification and encryption. This is similar to CVE-2021-23214 for PostgreSQL.

## References
- https://www.postgresql.org/support/security/CVE-2021-23214/
- https://github.com/yandex/odyssey/issues/376%2C
