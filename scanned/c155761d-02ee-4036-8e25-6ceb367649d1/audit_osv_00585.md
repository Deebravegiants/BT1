# [H] ALPINE-CVE-2017-17439

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-17439
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17439
Type: osv

## Affected
- Alpine:v3.10: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.11: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.12: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.13: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.14: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.15: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.16: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.17: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.18: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.19: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.20: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.21: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.22: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.23: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.24: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.6: `heimdal` — affected >=0 <7.1.0-r2
- Alpine:v3.7: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.8: `heimdal` — affected >=0 <7.4.0-r2
- Alpine:v3.9: `heimdal` — affected >=0 <7.4.0-r2

## Details
In Heimdal through 7.4, remote unauthenticated attackers are able to crash the KDC by sending a crafted UDP packet containing empty data fields for client name or realm. The parser would unconditionally dereference NULL pointers in that case, leading to a segmentation fault. This is related to the _kdc_as_rep function in kdc/kerberos5.c and the der_length_visible_string function in lib/asn1/der_length.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17439
