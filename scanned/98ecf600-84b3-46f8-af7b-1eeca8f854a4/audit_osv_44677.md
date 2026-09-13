# [M] MOOS-IvP through 24.8.1 pMarineViewer Unbounded Memory Consumption via NODE_REPORT

## Summary
Severity: Medium
Advisory: CVE-2026-85449
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85449
Type: osv

## Details
MOOS-IvP pMarineViewer through 24.8.1 fails to limit the number of tracked node identities from NODE_REPORT messages, allowing attackers to exhaust memory by supplying unbounded distinct node names. Attackers can publish crafted NODE_REPORT data to cause memory exhaustion and stall the operator display without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85449.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85449
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-pmarineviewer-unbounded-memory-consumption-via-node-report
- https://github.com/moos-ivp/moos-ivp/commit/4d8d0693d3f8bf8907dc0aed04ea488d85af9f22
- https://github.com/moos-ivp/moos-ivp/pull/134
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/lib_geodaid/ContactLedger.cpp#L186
