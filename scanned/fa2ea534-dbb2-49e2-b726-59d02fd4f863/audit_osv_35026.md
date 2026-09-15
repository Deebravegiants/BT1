# [M] Dify Vulnerable to Plaintext API Key Exposure via Model Provider Configuration Endpoint

## Summary
Severity: Medium
Advisory: CVE-2025-67732
Aliases: GHSA-phpv-94hg-fv9g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:L/SA:L)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-67732
Type: osv

## Details
Dify is an open-source LLM app development platform. Prior to version 1.11.0, the API key is exposed in plaintext to the frontend, allowing non-administrator users to view and reuse it. This can lead to unauthorized access to third-party services, potentially consuming limited quotas. Version 1.11.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67732.json
- https://github.com/langgenius/dify/security/advisories/GHSA-phpv-94hg-fv9g
- https://nvd.nist.gov/vuln/detail/CVE-2025-67732
