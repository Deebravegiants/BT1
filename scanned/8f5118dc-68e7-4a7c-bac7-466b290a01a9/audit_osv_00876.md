# [M] ALPINE-CVE-2018-1000654

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1000654
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000654
Type: osv

## Affected
- Alpine:v3.10: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.11: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.12: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.13: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.14: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.15: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.16: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.17: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.18: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.19: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.20: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.21: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.22: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.23: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.24: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.7: `libtasn1` — affected >=0 <4.12-r4
- Alpine:v3.8: `libtasn1` — affected >=0 <4.14-r0
- Alpine:v3.9: `libtasn1` — affected >=0 <4.14-r0

## Details
GNU Libtasn1-4.13 libtasn1-4.13 version libtasn1-4.13, libtasn1-4.12 contains a DoS, specifically CPU usage will reach 100% when running asn1Paser against the POC due to an issue in _asn1_expand_object_id(p_tree), after a long time, the program will be killed. This attack appears to be exploitable via parsing a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000654
