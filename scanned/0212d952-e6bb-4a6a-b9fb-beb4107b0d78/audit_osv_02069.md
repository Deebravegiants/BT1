# [M] ALPINE-CVE-2021-20254

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-20254
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-05-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20254
Type: osv

## Affected
- Alpine:v3.12: `samba` — affected >=3.6.0 <4.12.15-r0
- Alpine:v3.13: `samba` — affected >=3.6.0 <4.13.8-r0
- Alpine:v3.14: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.15: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.16: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.17: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.18: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.19: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.20: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.21: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.22: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.23: `samba` — affected >=3.6.0 <4.14.4-r0
- Alpine:v3.24: `samba` — affected >=3.6.0 <4.14.4-r0

## Details
A flaw was found in samba. The Samba smbd file server must map Windows group identities (SIDs) into unix group ids (gids). The code that performs this had a flaw that could allow it to read data beyond the end of the array in the case where a negative cache entry had been added to the mapping cache. This could cause the calling code to return those values into the process token that stores the group membership for a user. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20254
