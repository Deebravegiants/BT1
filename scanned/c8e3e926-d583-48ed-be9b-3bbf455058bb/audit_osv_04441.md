# [H] Bypass of email address validation via encoded email addresses in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2024-45051
Aliases: CVE-2024-45051, GHSA-2vjv-pgh4-6rmq
Ecosystem: Bitnami
Published: 2024-10-11
Source: https://osv.dev/vulnerability/BIT-discourse-2024-45051
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.3.2

## Details
Discourse is an open source platform for community discussion. A maliciously crafted email address could allow an attacker to bypass domain-based restrictions and gain access to private sites, categories and/or groups. This issue has been patched in the latest stable, beta and tests-passed version of Discourse. All users area are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-2vjv-pgh4-6rmq
- https://nvd.nist.gov/vuln/detail/CVE-2024-45051
