# [H] ALPINE-CVE-2021-3580

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3580
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3580
Type: osv

## Affected
- Alpine:v3.12: `nettle` — affected >=0 <3.5.1-r2
- Alpine:v3.13: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.14: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.15: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.16: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.17: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.18: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.19: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.20: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.21: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.22: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.23: `nettle` — affected >=0 <3.7.3-r0
- Alpine:v3.24: `nettle` — affected >=0 <3.7.3-r0

## Details
A flaw was found in the way nettle's RSA decryption functions handled specially crafted ciphertext. An attacker could use this flaw to provide a manipulated ciphertext leading to application crash and denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3580
