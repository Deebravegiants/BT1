# [M] OpenCTI: Elasticsearch Painless Script Injection via GraphQL `script` filter operator allows authenticated user to exfiltrate data and cause DoS

## Summary
Severity: Medium
Advisory: CVE-2026-35211
Aliases: GHSA-qpp6-p693-rmm4, PYSEC-2026-3446
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-35211
Type: osv

## Details
OpenCTI is an open source platform for managing cyber threat intelligence knowledge and observables. Prior to 7.260401.0, the OpenCTI GraphQL API exposes a script filter operator in its FilterOperator enum that allows any authenticated user with the KNOWLEDGE capability to pass user-supplied Elasticsearch Painless script values directly into search queries without validation or sanitization, allowing computationally expensive scripts to consume cluster CPU resources and degrade or deny service for all users. This issue is fixed in version 7.260401.0.

## References
- https://github.com/OpenCTI-Platform/opencti/releases/tag/7.260401.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35211.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-qpp6-p693-rmm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-35211
- https://github.com/OpenCTI-Platform/opencti/commit/b134ccedf9e68386723cb42197f8e1d60c3bdbd9
- https://github.com/OpenCTI-Platform/opencti/pull/15284
