# [H] n8n: Credential Exfiltration via Permission Bypass

## Summary
Severity: High
Advisory: GHSA-pmqw-72cg-wx85
CVE: CVE-2026-54307
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-pmqw-72cg-wx85
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.55
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=2.0.0-rc.0 <2.25.7

## Details
## Impact
A member-level user with editor access to a shared workflow could reference credentials they do not own via specific public API endpoints. Credential ownership checks were only enforced partially leading to cross-user credential access.

This issue affects instances where workflow sharing is enabled and at least one workflow has been shared with a member-level user as an Editor.

## Patches
The issue has been fixed in n8n versions 1.123.55, 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow sharing to fully trusted users only.
- Audit shared workflows for unexpected credential references or recent modifications.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backwards compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-pmqw-72cg-wx85
- https://nvd.nist.gov/vuln/detail/CVE-2026-54307
- https://github.com/n8n-io/n8n
