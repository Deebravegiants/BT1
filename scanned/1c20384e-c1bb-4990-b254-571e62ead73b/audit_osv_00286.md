# [H] ALPINE-CVE-2016-9296

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9296
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9296
Type: osv

## Affected
- Alpine:v3.10: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.11: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.12: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.13: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.14: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.15: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.16: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.17: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.5: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.6: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.7: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.8: `p7zip` — affected >=0 <16.02-r1
- Alpine:v3.9: `p7zip` — affected >=0 <16.02-r1

## Details
A null pointer dereference bug affects the 16.02 and many old versions of p7zip. A lack of null pointer check for the variable folders.PackPositions in function CInArchive::ReadAndDecodePackedStreams in CPP/7zip/Archive/7z/7zIn.cpp, as used in the 7z.so library and in 7z applications, will cause a crash and a denial of service when decoding malformed 7z files.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9296
