# [M] Discourse: Unauthorized channel membership inference via excluded_memberships_channel_id

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-32618
Aliases: CVE-2026-32618, GHSA-pc8p-w2m7-hgf3
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-32618
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, there is possible channel membership inference from chat user search without authorization. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/81fd89e744058e509412158e5e6ac90c856ade64
- https://github.com/discourse/discourse/security/advisories/GHSA-pc8p-w2m7-hgf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-32618
