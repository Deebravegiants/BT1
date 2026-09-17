# [H] Sub2API: Path traversal in the Responses subpath routes lets an authenticated tenant relay requests to arbitrary upstream endpoints using pooled account credentials

## Summary
Severity: High
Advisory: CVE-2026-73079
Aliases: GHSA-vrxq-qm4h-6hgg
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73079
Type: osv

## Details
Sub2API is an AI API gateway platform designed to distribute and manage API quotas from AI product subscriptions. From 0.1.135, to 0.1.168, platform API keys issued to tenants are exchanged for upstream requests made with shared provider accounts (ChatGPT/Codex OAuth, OpenAI platform keys, or an operator-configured base URL) that belong to the operator, not to the caller. The `POST /responses/*subpath` wildcard routes spliced the client-supplied subpath into the upstream URL with no validation. This lets an authenticated tenant relay requests to arbitrary upstream endpoints using pooled account credentials via a path traversal. This vulnerability is fixed in 0.1.169.

## References
- https://github.com/Wei-Shaw/sub2api/releases/tag/v0.1.169
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73079.json
- https://github.com/Wei-Shaw/sub2api/security/advisories/GHSA-vrxq-qm4h-6hgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-73079
- https://github.com/Wei-Shaw/sub2api/commit/017f6bbd5edffea0639ef3c84c0391161983f1f3
- https://github.com/Wei-Shaw/sub2api/pull/5137
