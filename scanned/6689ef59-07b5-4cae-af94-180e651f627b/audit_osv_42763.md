# [H] shiori - JWT CheckToken Never Re-Validates Account State, Allowing Stale-Privilege Access After Deletion or Demotion

## Summary
Severity: High
Advisory: CVE-2026-71206
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71206
Type: osv

## Details
Shiori's CheckToken function (internal/domains/auth.go) validates only the JWT's HMAC signature and returns the embedded claims.Account object unmodified, never re-fetching the account from the database. No session store or token-revocation mechanism exists in the codebase.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71206.json
- https://github.com/go-shiori/shiori
- https://nvd.nist.gov/vuln/detail/CVE-2026-71206
