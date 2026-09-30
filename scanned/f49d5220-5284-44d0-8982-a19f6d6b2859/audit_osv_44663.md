# [H] MOOS-IvP through 24.8.1 uFldNodeBroker Unauthenticated Shore Route Enrollment

## Summary
Severity: High
Advisory: CVE-2026-85435
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85435
Type: osv

## Details
MOOS-IvP uFldNodeBroker through 24.8.1 fails to validate the source of TRY_SHORE_HOST messages on the vehicle bus, allowing any publisher to enroll attacker-controlled shore routes. Attackers can publish malicious shore route messages to receive bridged vehicle traffic including sensor data and control information.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85435.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85435
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-ufldnodebroker-unauthenticated-shore-route-enrollment
- https://github.com/moos-ivp/moos-ivp/commit/d66394f576cae0c63c0a777760e1595802b83edf
- https://github.com/moos-ivp/moos-ivp/pull/124
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/uFldNodeBroker/NodeBroker.cpp#L97
