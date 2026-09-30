# [C] n8n: Expression Sandbox Escape Leads to RCE

## Summary
Severity: Critical
Advisory: GHSA-vpcf-gvg4-6qwr
CVE: CVE-2026-27577
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-vpcf-gvg4-6qwr
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.22
- npm: `n8n` — affected >=2.0.0 <2.9.3
- npm: `n8n` — affected >=2.10.0 <2.10.1

## Details
## Impact
Additional exploits in the expression evaluation of n8n have been identified and patched following [CVE-2025-68613](https://github.com/n8n-io/n8n/security/advisories/GHSA-v98v-ff95-f3cp). 
An authenticated user with permission to create or modify workflows could abuse crafted expressions in workflow parameters to trigger unintended system command execution on the host running n8n.

## Patches
The issues have been fixed in n8n versions 2.10.1, 2.9.3, and 1.123.22. Users should upgrade to one of these versions or later to remediate all known vulnerabilities.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Deploy n8n in a hardened environment with restricted operating system privileges and network access to reduce the impact of potential exploitation.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

### Resources
- Best practices for [securing n8n](https://docs.n8n.io/hosting/securing/overview/)
- Initial vulnerability advisory: [CVE-2025-68613](https://github.com/n8n-io/n8n/security/advisories/GHSA-v98v-ff95-f3cp)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-v98v-ff95-f3cp
- https://github.com/n8n-io/n8n/security/advisories/GHSA-vpcf-gvg4-6qwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27577
- https://github.com/n8n-io/n8n/commit/1479aab2d32fe0ee087f82b9038b1035c98be2f6
- https://github.com/n8n-io/n8n/commit/9e5212ecbc5d2d4e6f340b636a5e84be6369882e
- https://docs.n8n.io/hosting/securing/overview
- https://github.com/n8n-io/n8n
