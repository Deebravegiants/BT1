# [H] n8n Has External Secrets Authorization Bypass in Credential Saving

## Summary
Severity: High
Advisory: GHSA-fxcw-h3qj-8m8p
CVE: CVE-2026-33722
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-fxcw-h3qj-8m8p
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.23
- npm: `n8n` — affected >=2.0.0-rc.0 <2.6.4

## Details
## Impact
An authenticated user without permission to list external secrets could reference a secret by the external name in a credential and retrieve its plaintext value when saving the credential. This bypassed the `externalSecret:list` permission check and allowed access to secrets stored in connected vaults without admin or owner privileges.

- This issue requires the instance to have an external secrets vault configured.
- The attacker must know or be able to guess the name of a target secret.

## Patches
The issue has been fixed in n8n versions 1.123.23 and 2.6.4. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n access to fully trusted users only.
- Disable external secrets integration until the patch can be applied.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-fxcw-h3qj-8m8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33722
- https://github.com/n8n-io/n8n
