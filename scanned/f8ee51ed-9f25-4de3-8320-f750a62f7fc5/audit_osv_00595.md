# [H] ALPINE-CVE-2017-17969

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-17969
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17969
Type: osv

## Affected
- Alpine:v3.10: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.11: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.12: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.13: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.14: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.15: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.16: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.17: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.5: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.6: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.7: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.8: `p7zip` — affected >=0 <16.02-r2
- Alpine:v3.9: `p7zip` — affected >=0 <16.02-r2

## Details
Heap-based buffer overflow in the NCompress::NShrink::CDecoder::CodeReal method in 7-Zip before 18.00 and p7zip allows remote attackers to cause a denial of service (out-of-bounds write) or potentially execute arbitrary code via a crafted ZIP archive.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17969
