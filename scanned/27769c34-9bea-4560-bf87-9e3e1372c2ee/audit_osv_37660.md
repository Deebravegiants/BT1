# [C] AnythingLLM has a Streaming Phase XSS  to RCE via LLM Response Injection

## Summary
Severity: Critical
Advisory: CVE-2026-32626
Aliases: GHSA-rrmw-2j6x-4mf2
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32626
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. In 1.11.1 and earlier, AnythingLLM Desktop contains a Streaming Phase XSS vulnerability in the chat rendering pipeline that escalates to Remote Code Execution on the host OS due to insecure Electron configuration. This works with default settings and requires no user interaction beyond normal chat usage. The custom markdown-it image renderer in frontend/src/utils/chat/markdown.js interpolates token.content directly into the alt attribute without HTML entity escaping. The PromptReply component renders this output via dangerouslySetInnerHTML without DOMPurify sanitization — unlike HistoricalMessage which correctly applies DOMPurify.sanitize().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32626.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-rrmw-2j6x-4mf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32626
- https://github.com/Mintplex-Labs/anything-llm/commit/9e2d144dc8be6fab29f560f5bcdaa9ef7dbb4214
