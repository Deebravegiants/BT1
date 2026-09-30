# [M] MOOS-IvP through 24.8.1 pRealm Unbounded REALMCAST_REQ Subscription Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-85447
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85447
Type: osv

## Details
MOOS-IvP pRealm through version 24.8.1 accepts unbounded REALMCAST_REQ subscriptions without validating duration or variable list limits. Attackers can register long-lived pipeways with many variables to cause pRealm to generate excessive output indefinitely, exhausting system resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85447
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-prealm-unbounded-realmcast-req-subscription-denial-of-service
- https://github.com/moos-ivp/moos-ivp/commit/8a4bb9d9154a70e769a7290ee11dde5157c03e9b
- https://github.com/moos-ivp/moos-ivp/pull/132
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/pRealm/PipeWay.cpp#L109
