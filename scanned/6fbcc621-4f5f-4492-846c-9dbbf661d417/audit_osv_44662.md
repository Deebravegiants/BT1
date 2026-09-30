# [H] MOOS-IvP through 24.8.1 uFldShoreBroker Bridge Route Injection via Unverified Node Ping

## Summary
Severity: High
Advisory: CVE-2026-85434
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85434
Type: osv

## Details
MOOS-IvP uFldShoreBroker through 24.8.1 fails to verify node ping authenticity before creating outbound bridge routes. Attackers can publish NODE_BROKER_PING messages with crafted HostRecord data to redirect bridged variables to attacker-controlled addresses.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85434.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85434
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-ufldshorebroker-bridge-route-injection-via-unverified-node-ping
- https://github.com/moos-ivp/moos-ivp/commit/2f5224dcd68f92ce9ae10c261bb45dd7000f4d33
- https://github.com/moos-ivp/moos-ivp/pull/123
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/uFldShoreBroker/ShoreBroker.cpp#L93
