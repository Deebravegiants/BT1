# [H] PolarLearn's unvalidated vote direction allows vote count manipulation

## Summary
Severity: High
Advisory: CVE-2026-25126
Aliases: GHSA-ghpx-5w2p-p3qp
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-25126
Type: osv

## Details
PolarLearn is a free and open-source learning program. Prior to version 0-PRERELEASE-15, the vote API route (`POST /api/v1/forum/vote`) trusts the JSON body’s `direction` value without runtime validation. TypeScript types are not enforced at runtime, so an attacker can send arbitrary strings (e.g., `"x"`) as `direction`. Downstream (`VoteServer`) treats any non-`"up"` and non-`null` value as a downvote and persists the invalid value in `votes_data`. This can be exploited to bypass intended business logic. Version 0-PRERELEASE-15 fixes the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25126.json
- https://github.com/polarnl/PolarLearn/security/advisories/GHSA-ghpx-5w2p-p3qp
- https://nvd.nist.gov/vuln/detail/CVE-2026-25126
- https://github.com/polarnl/PolarLearn/commit/e6227d94d0e53e854f6a46480db8cd1051184d41
