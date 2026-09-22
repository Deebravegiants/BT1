# [H] ALPINE-CVE-2018-6003

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-6003
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6003
Type: osv

## Affected
- Alpine:v3.10: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.11: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.12: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.13: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.14: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.15: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.16: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.17: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.18: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.19: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.20: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.21: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.22: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.23: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.24: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.4: `libtasn1` — affected >=0 <4.8-r3
- Alpine:v3.5: `libtasn1` — affected >=0 <4.9-r3
- Alpine:v3.6: `libtasn1` — affected >=0 <4.10-r3
- Alpine:v3.7: `libtasn1` — affected >=0 <4.12-r3
- Alpine:v3.8: `libtasn1` — affected >=0 <4.13-r0
- Alpine:v3.9: `libtasn1` — affected >=0 <4.13-r0

## Details
An issue was discovered in the _asn1_decode_simple_ber function in decoding.c in GNU Libtasn1 before 4.13. Unlimited recursion in the BER decoder leads to stack exhaustion and DoS.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6003
