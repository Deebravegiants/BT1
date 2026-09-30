# [M] PM access granted through invites after access revocation

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33424
Aliases: CVE-2026-33424, GHSA-hgcp-p7hq-cwxw
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33424
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, an attacker can grant access to a private message topic through invites even after they lose access to that PM. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-hgcp-p7hq-cwxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33424
