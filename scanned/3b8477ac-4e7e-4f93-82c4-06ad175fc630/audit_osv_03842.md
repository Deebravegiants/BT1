# [M] ALPINE-CVE-2026-56116

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56116
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56116
Type: osv

## Affected
- Alpine:v3.23: `dhcpcd` — affected >=0 <10.5.2-r0
- Alpine:v3.24: `dhcpcd` — affected >=0 <10.5.2-r0

## Details
dhcpcd through 10.3.2, fixed in commit 708b4a5, contains a memory leak vulnerability in the IPv6 Router Advertisement route information handling that allows an unauthenticated same-link attacker to cause denial of service by sending crafted Router Advertisements. Attackers can repeatedly send Router Advertisements containing Route Information options with a lifetime of zero, triggering unfreed allocations in routeinfo_findalloc() that cause linear memory exhaustion and eventual daemon crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56116
