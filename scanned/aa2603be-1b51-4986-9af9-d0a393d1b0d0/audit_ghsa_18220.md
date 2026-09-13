# [M] FormCMS has an improper access control vulnerability in the /api/schemas/history/[schemaId] endpoint

## Summary
Severity: Medium
Advisory: GHSA-6cwx-42hw-w69c
CVE: CVE-2025-55797
CWE: CWE-200, CWE-284
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-6cwx-42hw-w69c
Type: github-advisory

## Affected
- NuGet: `FormCMS` — affected >=0 <0.5.5

## Details
An improper access control vulnerability in FormCms v0.5.4 in the /api/schemas/history/[schemaId] endpoint allows unauthenticated attackers to access historical schema data if a valid schemaId is known or guessed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55797
- https://github.com/formcms/formcms/issues/19
- https://github.com/FormCms
- https://github.com/FormCms/FormCms
- https://github.com/KKC73/me/tree/main/CVE-2025-55797
