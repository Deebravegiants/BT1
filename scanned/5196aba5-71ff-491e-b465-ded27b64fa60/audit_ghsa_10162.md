# [H] n8n's Credential Authorization Bypass in dynamic-node-parameters Allows Foreign API Key Replay

## Summary
Severity: High
Advisory: GHSA-r4v6-9fqc-w5jr
CVE: CVE-2026-42226
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-r4v6-9fqc-w5jr
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.17.0 <2.17.5
- npm: `n8n` — affected >=0 <1.123.33

## Details
## Impact
The `dynamic-node-parameters` endpoints did not verify whether the authenticated caller was authorized to use a supplied credential reference. An authenticated user with access to a shared workflow could supply a foreign credential ID in the request body, causing the backend to decrypt and use that credential in a helper execution path where the caller also controls the destination URL. This allowed the caller to force the backend to authenticate against attacker-controlled infrastructure using a credential belonging to another user, effectively exfiltrating a reusable API key.

The issue is not limited to any single node type; any node that resolves credentials dynamically through these endpoints may be affected.

## Patches
The issue has been fixed in n8n version 2.18.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n access to fully trusted users only.
- Avoid sharing workflows with users who should not have access to the credentials those workflows reference.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-r4v6-9fqc-w5jr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42226
- https://github.com/n8n-io/n8n
