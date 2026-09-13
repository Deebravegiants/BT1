# [M] Open WebUI: Any authenticated user can inject chats into another user's folder via chat completions

## Summary
Severity: Medium
Advisory: CVE-2026-87997
Aliases: GHSA-3pf7-q2g3-wj28
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87997
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.10.0 until 0.11.1, POST /api/chat/completions and POST /api/v1/chat/completions in backend/open_webui/main.py copied a client-supplied folder_id into a new chat without applying the folder write-access check used by the dedicated chat routes. An authenticated user who knew a shared folder identifier could inject an attacker-controlled chat into a folder where the user had read-only or no write access, causing the entry to appear to authorized folder readers. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87997.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3pf7-q2g3-wj28
- https://nvd.nist.gov/vuln/detail/CVE-2026-87997
- https://github.com/open-webui/open-webui/commit/d9e23b90c100d19b00270aea3cde0501d2354a6c
- https://github.com/open-webui/open-webui/pull/28366
