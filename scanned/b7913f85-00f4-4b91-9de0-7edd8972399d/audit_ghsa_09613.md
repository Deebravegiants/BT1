# [M] Langflow: DoS Through Lack of File Size Restriction via Deprecated Unauthenticated File Upload API

## Summary
Severity: Medium
Advisory: GHSA-vvfc-fp59-m92g
CVE: CVE-2026-6596
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-20
Source: https://github.com/advisories/GHSA-vvfc-fp59-m92g
Type: github-advisory

## Affected
- PyPI: `langflow-base` — affected >=0 <0.9.1

## Details
A security flaw has been discovered in langflow-ai langflow up to 1.1.0. This issue affects the function create_upload_file of the file src/backend/base/Langflow/api/v1/endpoints.py of the component API Endpoint. The manipulation results in unrestricted upload. It is possible to launch the attack remotely. The exploit has been released to the public and may be used for attacks. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6596
- https://github.com/langflow-ai/langflow/commit/b5662446bc8c54d928e278d3d26ad95b62425815
- https://gist.github.com/chenhouser2025/c2aabfdee41009cfe45d28a9924742a0
- https://github.com/langflow-ai/langflow
- https://github.com/langflow-ai/langflow/commits/v1.9.1
- https://vuldb.com/submit/791919
- https://vuldb.com/vuln/358231
- https://vuldb.com/vuln/358231/cti
