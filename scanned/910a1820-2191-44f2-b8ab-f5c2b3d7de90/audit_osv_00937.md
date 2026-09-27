# [H] ALPINE-CVE-2018-12020

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-12020
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12020
Type: osv

## Affected
- Alpine:v3.10: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.11: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.12: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.13: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.14: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.15: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.16: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.17: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.18: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.19: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.20: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.21: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.22: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.23: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.24: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.4: `gnupg` — affected >=0 <2.1.12-r1
- Alpine:v3.5: `gnupg` — affected >=0 <2.1.15-r1
- Alpine:v3.6: `gnupg` — affected >=0 <2.2.3-r1
- Alpine:v3.7: `gnupg` — affected >=0 <2.2.3-r1
- Alpine:v3.8: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.9: `gnupg` — affected >=0 <2.2.8-r0
- Alpine:v3.10: `gnupg1` — affected >=0 <1.4.22-r1
- Alpine:v3.11: `gnupg1` — affected >=0 <1.4.22-r1
- Alpine:v3.12: `gnupg1` — affected >=0 <1.4.22-r1
- Alpine:v3.5: `gnupg1` — affected >=0 <1.4.22-r1

## Details
mainproc.c in GnuPG before 2.2.8 mishandles the original filename during decryption and verification actions, which allows remote attackers to spoof the output that GnuPG sends on file descriptor 2 to other programs that use the "--status-fd 2" option. For example, the OpenPGP data might represent an original filename that contains line feed characters in conjunction with GOODSIG or VALIDSIG status codes.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12020
