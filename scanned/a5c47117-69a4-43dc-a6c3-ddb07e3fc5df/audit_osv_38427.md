# [M] TypeBot: Async filter() bypasses authorization, allowing IDOR in getLinkedTypebots and leaking cross-workspace bot definitions

## Summary
Severity: Medium
Advisory: CVE-2026-39966
Aliases: GHSA-3fr5-999r-84qj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-39966
Type: osv

## Details
TypeBot is a chatbot builder tool. In versions 3.15.2, the getLinkedTypebots API endpoint returns full bot definitions to any authenticated user who references a target bot ID in a Typebot Link block, regardless of workspace ownership, leading to IDOR. The authorization check uses Array.filter() with an async callback — since filter() is synchronous, the callback always returns a truthy Promise, so the access control predicate is never actually evaluated. Any authenticated Typebot user can read the full definition of any other workspace's private bots, including: all conversation blocks and logic flow, variable values embedded in the bot (credentials, API keys, PII), webhook URLs and integration configurations. This issue has been fixed in version 3.16.0.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39966.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-3fr5-999r-84qj
- https://nvd.nist.gov/vuln/detail/CVE-2026-39966
- https://github.com/baptisteArno/typebot.io/commit/b9530a089b43bfa6e79e3ff9cbfab921ce832f45
