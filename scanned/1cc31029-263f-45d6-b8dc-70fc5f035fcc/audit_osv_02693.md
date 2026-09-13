# [H] ALPINE-CVE-2022-42898

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42898
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42898
Type: osv

## Affected
- Alpine:v3.14: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.15: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.16: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.17: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.18: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.19: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.20: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.21: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.22: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.23: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.24: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.15: `krb5` — affected >=0 <1.19.4-r0
- Alpine:v3.16: `krb5` — affected >=0 <1.19.4-r0
- Alpine:v3.17: `krb5` — affected >=0 <1.20.1-r0
- Alpine:v3.18: `krb5` — affected >=0 <1.20.1-r0
- Alpine:v3.19: `krb5` — affected >=0 <1.20.1-r0
- Alpine:v3.20: `krb5` — affected >=0 <1.20.1-r0
- Alpine:v3.21: `krb5` — affected >=0 <1.20.1-r0
- Alpine:v3.22: `krb5` — affected >=0 <1.20.1-r0
- Alpine:v3.23: `krb5` — affected >=0 <1.20.1-r0
- Alpine:v3.24: `krb5` — affected >=0 <1.20.1-r0
- Alpine:v3.15: `samba` — affected >=4.16.0 <4.15.12-r0
- Alpine:v3.16: `samba` — affected >=4.16.0 <4.15.12-r0
- Alpine:v3.18: `samba` — affected >=4.16.0 <4.16.7-r0
- Alpine:v3.19: `samba` — affected >=4.16.0 <4.16.7-r0

## Details
PAC parsing in MIT Kerberos 5 (aka krb5) before 1.19.4 and 1.20.x before 1.20.1 has integer overflows that may lead to remote code execution (in KDC, kadmind, or a GSS or Kerberos application server) on 32-bit platforms (which have a resultant heap-based buffer overflow), and cause a denial of service on other platforms. This occurs in krb5_pac_parse in lib/krb5/krb/pac.c. Heimdal before 7.7.1 has "a similar bug."

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42898
