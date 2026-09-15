# [M] discourse-subscriptions plugin leaking stripe API key in multisite environment

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33073
Aliases: CVE-2026-33073, GHSA-f866-8fcp-fgvv
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33073
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, the discourse-subscriptions plugin leaks stripe API keys across sites in a multisite cluster resulting in the potential for stripe related information to be leaked across sites within the same multisite cluster. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/c34f2aac8dcd1ae2886fa84256f607bc003f9d80
- https://github.com/discourse/discourse/security/advisories/GHSA-f866-8fcp-fgvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33073
