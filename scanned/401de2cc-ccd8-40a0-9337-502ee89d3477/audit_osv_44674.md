# [M] MOOS-IvP through 24.8.1 uFldNodeComms Quadratic Processing Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-85446
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85446
Type: osv

## Details
MOOS-IvP versions through 24.8.1 contain a quadratic processing vulnerability in uFldNodeComms where each new node identity creates a ledger entry and triggers all-pairs distribution work. Attackers can supply unbounded distinct node names in reports to drive the shoreside broker into quadratic processing, delaying or preventing distribution of legitimate node reports.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85446.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85446
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-ufldnodecomms-quadratic-processing-denial-of-service
- https://github.com/moos-ivp/moos-ivp/commit/8e30008d4eb68d83797187bd46e929e6cb06b195
- https://github.com/moos-ivp/moos-ivp/pull/131
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/uFldNodeComms/FldNodeComms.cpp#L169
