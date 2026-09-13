# [M] The coturn server can end in a state where it does not accept more requests with "even-port" enabled.

## Summary
Severity: Medium
Advisory: CVE-2026-73215
Aliases: GHSA-847g-qmc6-6m4r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73215
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.17.0, turnports_allocate_even() in src/apps/relay/turn_ports.c marks the unused odd sibling port as TPS_TAKEN_ODD for an EVEN-PORT Allocate request with reservation bit R=0 even though no RTCP socket will release it, allowing an authenticated client to permanently exhaust the relay port pool and cause subsequent allocations to fail with STUN error 508. This issue is fixed in version 4.17.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73215.json
- https://github.com/coturn/coturn/security/advisories/GHSA-847g-qmc6-6m4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-73215
- https://github.com/coturn/coturn/commit/4adbd82e78456e13109bf44deed4ec3aceb0bab2
