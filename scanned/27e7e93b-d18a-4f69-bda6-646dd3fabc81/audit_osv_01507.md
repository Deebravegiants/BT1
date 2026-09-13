# [H] ALPINE-CVE-2019-1789

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-1789
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1789
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.6: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.7: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.100.3-r0

## Details
ClamAV versions prior to 0.101.2 are susceptible to a denial of service (DoS) vulnerability. An out-of-bounds heap read condition may occur when scanning PE files. An example is Windows EXE and DLL files that have been packed using Aspack as a result of inadequate bound-checking.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1789
