# [H] prompts.chat Identity Confusion via Case-Sensitive Username Handling

## Summary
Severity: High
Advisory: CVE-2026-22665
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-22665
Type: osv

## Details
prompts.chat prior to commit 1464475, contains an identity confusion vulnerability due to inconsistent case-sensitive and case-insensitive handling of usernames across write and read paths, allowing attackers to create case-variant usernames that bypass uniqueness checks. Attackers can exploit non-deterministic username resolution to impersonate victim accounts, replace profile content on canonical URLs, and inject attacker-controlled metadata and content across the platform.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22665.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22665
- https://www.vulncheck.com/advisories/prompts-chat-identity-confusion-via-case-sensitive-username-handling
- https://github.com/f/prompts.chat/pull/1098
- https://github.com/f/prompts.chat/commit/1464475df2698fb7ccd0cdbc382b0750466f891d
- https://github.com/f/prompts.chat
