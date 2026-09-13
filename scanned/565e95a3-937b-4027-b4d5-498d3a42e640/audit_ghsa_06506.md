# [M] n8n: External Secrets Permission Bypass via Expression Parser Mismatch

## Summary
Severity: Medium
Advisory: GHSA-jp7m-xcgx-57qm
CVE: CVE-2026-59259
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-jp7m-xcgx-57qm
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.61
- npm: `n8n` — affected >=2.28.0 <2.28.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.27.4

## Details
## Impact
Due to a mismatch between the static validation check and the runtime expression engine, an authenticated user with credential create or update permissions, but without the `externalSecret:list` scope, could embed external secret references into credentials in forms the validation did not detect. These references would resolve at workflow execution time, exposing secret values the user was not authorized to access.

This issue only affects instances where an external secrets provider is configured and Advanced Permissions are in use.

## Patches
The issue has been fixed in n8n versions 1.123.61, 2.27.4, and 2.28.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict credential creation and update permissions to fully trusted users only.
- Audit existing credentials for unexpected external secret references.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jp7m-xcgx-57qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-59259
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.61
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.27.4
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.28.1
- https://www.vulncheck.com/advisories/n8n-permission-bypass-via-expression-parser-mismatch-in-external-secrets
