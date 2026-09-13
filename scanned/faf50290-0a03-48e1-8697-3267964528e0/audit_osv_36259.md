# [H] prompts.chat Path Traversal via Skill File Handling

## Summary
Severity: High
Advisory: CVE-2026-22661
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-22661
Type: osv

## Details
prompts.chat prior to commit 0f8d4c3 contains a path traversal vulnerability in skill file handling that allows attackers to write arbitrary files to the client system by crafting malicious ZIP archives with unsanitized filenames containing path traversal sequences. Attackers can exploit missing server-side filename validation to inject path traversal sequences ../ into skill file archives, which when extracted by vulnerable tools writing files outside the intended directory and overwriting shell initialization files to achieve code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22661.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22661
- https://www.vulncheck.com/advisories/prompts-chat-path-traversal-via-skill-file-handling
- https://github.com/f/prompts.chat/pull/1101
- https://github.com/f/prompts.chat/commit/0f8d4c381abd7b2d7478c9fdee9522149c2d65e5
- https://github.com/f/prompts.chat
