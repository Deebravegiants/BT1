# [C] FinalDestination hostname matching allows SSRF protection bypass

## Summary
Severity: Critical
Advisory: BIT-discourse-2025-68662
Aliases: CVE-2025-68662, GHSA-gcfp-rjfc-925c
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-68662
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, a hostname validation issue in FinalDestination could allow bypassing SSRF protections under certain conditions. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-gcfp-rjfc-925c
- https://nvd.nist.gov/vuln/detail/CVE-2025-68662
