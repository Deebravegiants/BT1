# [M] Discourse: Unauthorized eavesdropping on private AI bot conversations.

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-72726
Aliases: CVE-2026-72726, GHSA-gw88-2jw8-jf2h
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-discourse-2026-72726
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.6.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0, an authenticated user could eavesdrop on private AI bot conversations through the AI bot reply stream. The issue is fixed in 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0.

## References
- https://github.com/discourse/discourse/commit/01faa889830f56e02fba2f6c1731811d319c5e81
- https://github.com/discourse/discourse/commit/1fb2026eb8004dfeb12553014cc534dfd8083fbc
- https://github.com/discourse/discourse/commit/9247666f8359f3cf214b8aea3d396e8a8237ed38
- https://github.com/discourse/discourse/commit/b56b98232aa4dad4a30500a65e31db0c9080c8f5
- https://github.com/discourse/discourse/security/advisories/GHSA-gw88-2jw8-jf2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-72726
