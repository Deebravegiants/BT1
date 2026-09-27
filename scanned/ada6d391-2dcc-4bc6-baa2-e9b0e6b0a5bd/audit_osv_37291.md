# [C] WeKnora: Remote Code Execution via SQL Injection Bypass in AI Database Query Tool

## Summary
Severity: Critical
Advisory: CVE-2026-30860
Aliases: GHSA-8w32-6mrw-q5wv, GO-2026-4641
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-30860
Type: osv

## Details
WeKnora is an LLM-powered framework designed for deep document understanding and semantic retrieval. Prior to version 0.2.12, a remote code execution (RCE) vulnerability exists in the application's database query functionality. The validation system fails to recursively inspect child nodes within PostgreSQL array expressions and row expressions, allowing attackers to bypass SQL injection protections. By smuggling dangerous PostgreSQL functions inside these expressions and chaining them with large object operations and library loading capabilities, an unauthenticated attacker can achieve arbitrary code execution on the database server with database user privileges. This issue has been patched in version 0.2.12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30860.json
- https://github.com/Tencent/WeKnora/security/advisories/GHSA-8w32-6mrw-q5wv
- https://nvd.nist.gov/vuln/detail/CVE-2026-30860
