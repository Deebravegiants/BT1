# [M] n8n's Source Control SSH Configuration Uses StrictHostKeyChecking=no

## Summary
Severity: Medium
Advisory: GHSA-43v7-fp2v-68f6
CVE: CVE-2026-33724
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-43v7-fp2v-68f6
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.5.0

## Details
## Impact
When the Source Control feature is configured to use SSH, the SSH command used for git operations explicitly disabled host key verification. A network attacker positioned between the n8n instance and the remote Git server could intercept the connection and present a fraudulent host key, potentially injecting malicious content into workflows or intercepting repository data.

- This issue only affects instances where the Source Control feature has been explicitly enabled and configured to use SSH (non-default).

## Patches
The issue has been fixed in n8n version 2.5.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable the Source Control feature if it is not actively required.
- Restrict network access to ensure the n8n instance communicates with the Git server only over trusted, controlled network paths.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-43v7-fp2v-68f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33724
- https://github.com/n8n-io/n8n
