# [H] ALPINE-CVE-2019-11745

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-11745
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11745
Type: osv

## Affected
- Alpine:v3.10: `nss` — affected >=0 <3.44.3-r0
- Alpine:v3.11: `nss` — affected >=0 <3.47.1-r0
- Alpine:v3.12: `nss` — affected >=0 <3.47.1-r0
- Alpine:v3.19: `nss` — affected >=0 <3.47.1-r0
- Alpine:v3.20: `nss` — affected >=0 <3.47.1-r0
- Alpine:v3.21: `nss` — affected >=0 <3.47.1-r0
- Alpine:v3.22: `nss` — affected >=0 <3.47.1-r0
- Alpine:v3.23: `nss` — affected >=0 <3.47.1-r0
- Alpine:v3.24: `nss` — affected >=0 <3.47.1-r0

## Details
When encrypting with a block cipher, if a call to NSC_EncryptUpdate was made with data smaller than the block size, a small out of bounds write could occur. This could have caused heap corruption and a potentially exploitable crash. This vulnerability affects Thunderbird < 68.3, Firefox ESR < 68.3, and Firefox < 71.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11745
