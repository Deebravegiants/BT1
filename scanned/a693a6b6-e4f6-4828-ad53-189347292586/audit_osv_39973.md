# [M] TypeBot Vulnerable to Server-Side Request Forgery (SSRF) in OpenAI Transcription Handler

## Summary
Severity: Medium
Advisory: CVE-2026-48762
Aliases: GHSA-h3v3-c6cq-q763
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48762
Type: osv

## Details
TypeBot is a chatbot builder tool. Prior to version 3.16.0, the OpenAI "Create Transcription" action handler fetches a user-supplied audio URL using `fetch()` without applying the SSRF protection that exists elsewhere in the codebase. An attacker can direct the server to make HTTP requests to arbitrary internal addresses and localhost. The fetched content is passed to the OpenAI Whisper API and the transcription result is returned to the attacker. Version 3.16.0 fixes the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48762.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-h3v3-c6cq-q763
- https://nvd.nist.gov/vuln/detail/CVE-2026-48762
- https://github.com/baptisteArno/typebot.io/commit/a33051755f9e734596498851d5f61bd2e171f192
- https://github.com/baptisteArno/typebot.io/pull/2428
