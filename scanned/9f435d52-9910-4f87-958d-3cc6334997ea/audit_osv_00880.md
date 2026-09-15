# [H] ALPINE-CVE-2018-10115

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-10115
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10115
Type: osv

## Affected
- Alpine:v3.10: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.11: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.12: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.13: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.14: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.15: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.16: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.17: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.5: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.6: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.7: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.8: `p7zip` — affected >=0 <16.02-r3
- Alpine:v3.9: `p7zip` — affected >=0 <16.02-r3

## Details
Incorrect initialization logic of RAR decoder objects in 7-Zip 18.03 and before can lead to usage of uninitialized memory, allowing remote attackers to cause a denial of service (segmentation fault) or execute arbitrary code via a crafted RAR archive.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10115
