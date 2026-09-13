# [H] FreshRSS has an IDOR which allows for viewing feeds of any user and leaking tokens

## Summary
Severity: High
Advisory: CVE-2025-62166
Aliases: GHSA-w743-fg6g-mhwh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2025-62166
Type: osv

## Details
FreshRSS is a free, self-hostable RSS aggregator. Prior 1.28.0, a bug in the auth logic related to master authentication tokens, this restriction is bypassed. Usually only the default user's feed should be viewable if anonymous viewing is enabled, and feeds of other users should be private. This vulnerability is fixed in 1.28.0.

## References
- https://github.com/FreshRSS/FreshRSS/releases/tag/1.28.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62166.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-w743-fg6g-mhwh
- https://nvd.nist.gov/vuln/detail/CVE-2025-62166
- https://github.com/FreshRSS/FreshRSS/commit/60cf5ea297a17db861e73cd65d7b7862bd6bcc24
- https://github.com/FreshRSS/FreshRSS/pull/8165
