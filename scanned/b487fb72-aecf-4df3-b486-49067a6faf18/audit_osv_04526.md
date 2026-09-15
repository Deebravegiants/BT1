# [M] Discourse: Group SMTP test endpoint susceptible to SSRF

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33185
Aliases: CVE-2026-33185, GHSA-5976-77mj-m4h3
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33185
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, the group email settings test endpoint could be used to make the server initiate outbound connections to arbitrary hosts and ports. This could allow probing of internal network infrastructure. The endpoint was accessible to non-staff group owners. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/e75cf456e8e318290c569bd6e8fa0f2586ffc530
- https://github.com/discourse/discourse/security/advisories/GHSA-5976-77mj-m4h3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33185
