# [H] ALPINE-CVE-2017-9789

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9789
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9789
Type: osv

## Affected
- Alpine:v3.3: `apache2` — affected >=0 <2.4.27-r0
- Alpine:v3.4: `apache2` — affected >=0 <2.4.27-r0
- Alpine:v3.5: `apache2` — affected >=0 <2.4.27-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.27-r0

## Details
When under stress, closing many connections, the HTTP/2 handling code in Apache httpd 2.4.26 would sometimes access memory after it has been freed, resulting in potentially erratic behaviour.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9789
