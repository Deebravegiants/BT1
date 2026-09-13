# [M] MOOS-IvP through 24.8.1 uFldNodeComms Node Message Source Spoofing

## Summary
Severity: Medium
Advisory: CVE-2026-85429
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85429
Type: osv

## Details
MOOS-IvP uFldNodeComms through 24.8.1 trusts the source node identity from the message body rather than validating it from the connection source. Attackers can craft NODE_MESSAGE packets with spoofed source identities to impersonate other nodes and post arbitrary variable notifications without validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85429.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85429
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-ufldnodecomms-node-message-source-spoofing
- https://github.com/moos-ivp/moos-ivp/commit/3907ac07cdfd8a7255d65657dc18dc6b77b30b64
- https://github.com/moos-ivp/moos-ivp/pull/122
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/uFldNodeComms/FldNodeComms.cpp#L114
