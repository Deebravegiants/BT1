# [M] ALPINE-CVE-2025-11411

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-11411
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:H/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-11411
Type: osv

## Affected
- Alpine:v3.19: `unbound` — affected >=0 <1.20.0-r2
- Alpine:v3.20: `unbound` — affected >=0 <1.20.0-r2
- Alpine:v3.21: `unbound` — affected >=0 <1.22.0-r1
- Alpine:v3.22: `unbound` — affected >=0 <1.23.1-r1
- Alpine:v3.23: `unbound` — affected >=0 <1.24.1-r0
- Alpine:v3.24: `unbound` — affected >=0 <1.24.1-r0

## Details
NLnet Labs Unbound up to and including version 1.24.1 is vulnerable to possible domain hijack attacks. Promiscuous NS RRSets that complement positive DNS replies in the authority section can be used to trick resolvers to update their delegation information for the zone. Usually these RRSets are used to update the resolver's knowledge of the zone's name servers. A malicious actor can exploit the possible poisonous effect by injecting NS RRSets (and possibly their respective address records) in a reply. This could be done for example by trying to spoof a packet or fragmentation attacks. Unbound would then proceed to update the NS RRSet data it already has since the new data has enough trust for it, i.e., in-zone data for the delegation point. Unbound 1.24.1 includes a fix that scrubs unsolicited NS RRSets (and their respective address records) from replies mitigating the possible poison effect. Unbound 1.24.2 includes an additional fix that scrubs unsolicited NS RRSets (and their respective address records) from YXDOMAIN and non-referral nodata replies, further mitigating the possible poison effect.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-11411
