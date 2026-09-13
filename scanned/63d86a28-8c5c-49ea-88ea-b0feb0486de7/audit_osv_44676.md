# [M] MOOS-IvP through 24.8.1 uFldShoreBroker Unbounded Community State Retention

## Summary
Severity: Medium
Advisory: CVE-2026-85448
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85448
Type: osv

## Details
MOOS-IvP uFldShoreBroker through 24.8.1 fails to limit the number of claimed communities stored in parallel vectors within ShoreBroker::handleMailNodePing(). A single publisher can supply unbounded distinct community names to grow retained state and per-pass work without limit, causing memory exhaustion and performance degradation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85448.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85448
- https://www.vulncheck.com/advisories/moos-ivp-through-24.8.1-ufldshorebroker-unbounded-community-state-retention
- https://github.com/moos-ivp/moos-ivp/commit/2cbaed2227db31f50d5542cafe08445596800801
- https://github.com/moos-ivp/moos-ivp/pull/133
- https://github.com/moos-ivp/moos-ivp
- https://github.com/moos-ivp/moos-ivp/blob/1de9ae146cd63c209e8c3fd81611a4ed2472971b/ivp/src/uFldShoreBroker/ShoreBroker.cpp#L124
