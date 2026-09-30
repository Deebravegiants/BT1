# [M] ALPINE-CVE-2025-5994

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-5994
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:U/V:C/RE:X/U:X)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-5994
Type: osv

## Affected
- Alpine:v3.19: `unbound` — affected >=0 <1.20.0-r2
- Alpine:v3.20: `unbound` — affected >=0 <1.20.0-r2
- Alpine:v3.21: `unbound` — affected >=0 <1.22.0-r1
- Alpine:v3.22: `unbound` — affected >=0 <1.23.1-r0
- Alpine:v3.23: `unbound` — affected >=0 <1.23.1-r0
- Alpine:v3.24: `unbound` — affected >=0 <1.23.1-r0

## Details
A multi-vendor cache poisoning vulnerability named 'Rebirthday Attack' has been discovered in caching resolvers that support EDNS Client Subnet (ECS). Unbound is also vulnerable when compiled with ECS support, i.e., '--enable-subnet', AND configured to send ECS information along with queries to upstream name servers, i.e., at least one of the 'send-client-subnet', 'client-subnet-zone' or 'client-subnet-always-forward' options is used. Resolvers supporting ECS need to segregate outgoing queries to accommodate for different outgoing ECS information. This re-opens up resolvers to a birthday paradox attack (Rebirthday Attack) that tries to match the DNS transaction ID in order to cache non-ECS poisonous replies.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-5994
