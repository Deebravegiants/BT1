# [M] Discourse has a Hidden Solved topics permission bypass

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33251
Aliases: CVE-2026-33251, GHSA-vm2x-9h8x-7jxm
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33251
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, an authorization bypass vulnerability in hidden Solved topics may allow unauthorized users to accept or unaccept solutions. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. As a workaround, ensure only trusted users are part of the Site Setting for accept_all_solutions_allowed_groups.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-vm2x-9h8x-7jxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33251
