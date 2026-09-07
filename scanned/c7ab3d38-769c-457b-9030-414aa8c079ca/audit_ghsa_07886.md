# [H] n8n Has Stored Cross-site Scripting via Markdown Rendering in Workflow UI

## Summary
Severity: High
Advisory: GHSA-qpq4-pw7f-pp8w
CVE: CVE-2026-25054
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-qpq4-pw7f-pp8w
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.0.0 <2.2.1
- npm: `n8n` — affected >=0 <1.123.9

## Details
## Impact
A Cross-site Scripting (XSS) vulnerability existed in a markdown rendering component used in n8n's interface, including workflow sticky notes and other areas that support markdown content.

An authenticated user with permission to create or modify workflows could abuse this to execute scripts with same-origin privileges when other users interact with a maliciously crafted workflow. This could lead to session hijacking and account takeover.

## Patches
The issue has been fixed in n8n versions 2.2.1 and 1.123.9. Users should upgrade to these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Review existing workflows for potentially malicious markdown content in sticky notes and other components.
- Educate users about the risks of opening workflows from untrusted sources.
These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backward compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-qpq4-pw7f-pp8w
- https://nvd.nist.gov/vuln/detail/CVE-2026-25054
- https://github.com/n8n-io/n8n
