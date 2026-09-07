# [M] Stored XSS in n8n LangChain Chat Trigger Node via initialMessages Parameter

## Summary
Severity: Medium
Advisory: GHSA-mvh4-2cm2-6hpg
CVE: CVE-2025-58177
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-mvh4-2cm2-6hpg
Type: github-advisory

## Affected
- npm: `n8n` — affected >=1.24.0 <1.107.0

## Details
### Impact
A stored Cross-Site Scripting (XSS) vulnerability was identified in the `@n8n/n8n-nodes-langchain.chatTrigger` node in n8n. If an authorized user configures the node with malicious JavaScript in the initialMessages field and enables public access, the script will be executed in the browser of anyone who visits the resulting public chat URL.

This vulnerability could be exploited for phishing or to steal cookies or other sensitive data from users who access the public chat link, posing a security risk.

### Patches
This issue has been patched in version 1.107.0 of n8n. Users should upgrade to version 1.107.0 or later.

### Workarounds
Disabling the `n8n-nodes-langchain.chatTrigger` node ([docs](https://docs.n8n.io/hosting/securing/blocking-nodes/))

### References
#18148

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-mvh4-2cm2-6hpg
- https://nvd.nist.gov/vuln/detail/CVE-2025-58177
- https://github.com/n8n-io/n8n/pull/18148
- https://github.com/n8n-io/n8n/commit/d4ef191be0b39b65efa68559a3b8d5dad2e102b2
- https://docs.n8n.io/hosting/securing/blocking-nodes
- https://github.com/n8n-io/n8n
