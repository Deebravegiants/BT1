# [H] rsync 3.1.0 < 3.5.0 Authorization Bypass via auth users Directive Parsing

## Summary
Severity: High
Advisory: CVE-2026-70463
Aliases: GHSA-pfj8-79vq-xgvr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70463
Type: osv

## Details
rsync 3.1.0 before 3.5.0 contains an authorization bypass in auth users directive parsing. The auth users parser uses comma-only tokenization when splitting the user list, which fails to correctly handle entries of the form @Group Name where the group name contains a space. The space within the group name causes the parser to split the entry at the space boundary, discarding the deny rule associated with the group. An authenticated user whose username or group membership would be denied by an @Group Name auth users entry can connect to a restricted module because the deny rule is silently discarded during parsing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70463.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-pfj8-79vq-xgvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-70463
- https://www.vulncheck.com/advisories/rsync-authorization-bypass-via-auth-users-directive-parsing
- https://github.com/RsyncProject/rsync
