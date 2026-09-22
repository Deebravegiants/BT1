# [M] ALPINE-CVE-2024-0684

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-0684
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-0684
Type: osv

## Affected
- Alpine:v3.18: `coreutils` — affected >=0 <9.3-r2
- Alpine:v3.19: `coreutils` — affected >=0 <9.4-r2
- Alpine:v3.20: `coreutils` — affected >=0 <9.4-r2
- Alpine:v3.21: `coreutils` — affected >=0 <9.4-r2
- Alpine:v3.22: `coreutils` — affected >=0 <9.4-r2
- Alpine:v3.23: `coreutils` — affected >=0 <9.4-r2
- Alpine:v3.24: `coreutils` — affected >=0 <9.4-r2

## Details
A flaw was found in the GNU coreutils "split" program. A heap overflow with user-controlled data of multiple hundred bytes in length could occur in the line_bytes_split() function, potentially leading to an application crash and denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-0684
