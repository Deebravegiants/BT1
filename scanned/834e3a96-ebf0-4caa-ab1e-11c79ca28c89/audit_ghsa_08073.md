# [M] Cloudflare Agents SDK has Insecure Direct Object Reference (IDOR) via Header-Based Email Routing

## Summary
Severity: Medium
Advisory: GHSA-r7x9-8ph7-w8cg
CVE: CVE-2026-1664
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-r7x9-8ph7-w8cg
Type: github-advisory

## Affected
- npm: `agents` — affected >=0 <0.3.7

## Details
### Summary
An Insecure Direct Object Reference (CWE-639) has been found to exist in createHeaderBasedEmailResolver() function within the Cloudflare Agents SDK. The issue occurs because the Message-ID and References headers are parsed to derive the target agentName and agentId without proper validation or origin checks, allowing an external attacker with control of these headers to route inbound mail to arbitrary Durable Object instances and namespaces.

### Root cause
The createHeaderBasedEmailResolver() function lacks cryptographic verification or origin validation for the headers used in the routing logic, effectively allowing external input to dictate internal object routing.

### Impact
Insecure Direct Object Reference (IDOR) in email routing lets an attacker steer inbound mail to arbitrary Agent instances via spoofed Message-ID.



### Patches
Agents-sdk users should  upgrade to agents@0.3.7. 
PR: https://github.com/cloudflare/agents/pull/811
This [documentation](https://github.com/cloudflare/agents/blob/main/docs/email.md) provides the necessary architectural context for coding agents to mitigate the issue by refactoring the resolver to enforce strict identity boundaries.

## References
- https://github.com/cloudflare/agents/security/advisories/GHSA-r7x9-8ph7-w8cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-1664
- https://github.com/cloudflare/agents
- https://github.com/cloudflare/agents/blob/main/docs/email.md
