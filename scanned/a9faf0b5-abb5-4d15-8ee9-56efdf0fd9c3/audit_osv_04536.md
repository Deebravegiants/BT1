# [M] Discourse exposes ip_address of flagged user

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33422
Aliases: CVE-2026-33422, GHSA-x32r-45vg-vm84
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33422
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, the `ip_address` of a flagged user is exposed to any user who can access the review queue, including users who should not be able to see IP addresses. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-x32r-45vg-vm84
- https://nvd.nist.gov/vuln/detail/CVE-2026-33422
