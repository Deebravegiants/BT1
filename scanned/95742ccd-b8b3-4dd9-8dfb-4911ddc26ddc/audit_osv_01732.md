# [C] ALPINE-CVE-2020-12403

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-12403
Ecosystem: Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-12403
Type: osv

## Affected
- Alpine:v3.12: `nss` — affected >=0 <3.55-r0
- Alpine:v3.19: `nss` — affected >=0 <3.55-r0
- Alpine:v3.20: `nss` — affected >=0 <3.55-r0
- Alpine:v3.21: `nss` — affected >=0 <3.55-r0
- Alpine:v3.22: `nss` — affected >=0 <3.55-r0
- Alpine:v3.23: `nss` — affected >=0 <3.55-r0
- Alpine:v3.24: `nss` — affected >=0 <3.55-r0

## Details
A flaw was found in the way CHACHA20-POLY1305 was implemented in NSS in versions before 3.55. When using multi-part Chacha20, it could cause out-of-bounds reads. This issue was fixed by explicitly disabling multi-part ChaCha20 (which was not functioning correctly) and strictly enforcing tag length. The highest threat from this vulnerability is to confidentiality and system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-12403
