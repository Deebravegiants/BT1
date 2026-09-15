# [H] Discourse Authorization Page Displays Unvalidated Redirect Domain

## Summary
Severity: High
Advisory: BIT-discourse-2026-33427
Aliases: CVE-2026-33427, GHSA-9vhg-2mx3-mqfr
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33427
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, an unauthenticated attacker can cause a legitimate Discourse authorization page to display an attacker-controlled domain, facilitating social engineering attacks against users. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-9vhg-2mx3-mqfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33427
