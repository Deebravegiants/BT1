# [H] ALPINE-CVE-2019-12098

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12098
Ecosystem: Alpine:v3.10, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-05-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12098
Type: osv

## Affected
- Alpine:v3.10: `heimdal` — affected >=0 <7.5.0-r5
- Alpine:v3.7: `heimdal` — affected >=0 <7.4.0-r4
- Alpine:v3.8: `heimdal` — affected >=0 <7.5.0-r3
- Alpine:v3.9: `heimdal` — affected >=0 <7.5.0-r4

## Details
In the client side of Heimdal before 7.6.0, failure to verify anonymous PKINIT PA-PKINIT-KX key exchange permits a man-in-the-middle attack. This issue is in krb5_init_creds_step in lib/krb5/init_creds_pw.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12098
