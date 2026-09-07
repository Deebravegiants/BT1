# [H] n8n's Improper CSP Enforcement in Webhook Responses May Allow Stored XSS

## Summary
Severity: High
Advisory: GHSA-825q-w924-xhgx
CVE: CVE-2026-25051
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-825q-w924-xhgx
Type: github-advisory

## Affected
- npm: `n8n` — affected >=1.123.0 <1.123.2
- npm: `n8n` — affected >=0 <1.122.5

## Details
## Impact

A Cross-site Scripting (XSS) vulnerability has been identified in the handling of webhook responses and related HTTP endpoints. Under certain conditions, the Content Security Policy (CSP) sandbox protection intended to isolate HTML responses may not be applied correctly.

An authenticated user with permission to create or modify workflows could abuse this to execute malicious scripts with same-origin privileges when other users interact with the crafted workflow. This could lead to session hijacking and account takeover.

## Patches

The issue has been fixed in n8n versions 1.122.5 and 1.123.2. Users should upgrade to these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:

- Limit workflow creation and editing permissions to fully trusted users only.
- Never execute untrusted workflows.
- Review workflows that receive data from via webhooks, forms, or MCP servers to ensure they are communicating with trusted entities before executing them manually.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backward compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-825q-w924-xhgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-25051
- https://github.com/n8n-io/n8n/commit/ced34c0f93ab4c759a56065965986094d8ef7323
- https://github.com/n8n-io/n8n/commit/e8cf4d6bb3af94dc296cbb67bc3dd20e9b508ac9
- https://github.com/n8n-io/n8n
