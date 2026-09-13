# [M] Nextcloud: Propfind requests for file comments allowed to load comments for other files

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2026-45810
Aliases: CVE-2026-45810, GHSA-285v-p9x9-cjhj
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2026-45810
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=32.0.0 <32.0.3

## Details
Nextcloud is an open source content collaboration platform. In Nextcloud Server from versions 31.0.0 to before 31.0.12, and 32.0.0 to before 32.0.3, a missing check of a relation allowed authenticated users with access to any file comment, to read the content of all comments. It is recommended that the Nextcloud Server is upgraded to 31.0.12 or 32.0.3. It is recommended that the Nextcloud Enterprise Server is upgraded to 21.0.9.20, 22.2.10.35, 23.0.12.31, 24.0.12.30, 25.0.13.25, 26.0.13.22, 27.1.11.22, 28.0.14.13, 29.0.16.10, 30.0.17.5, 31.0.12 or 32.0.3

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-285v-p9x9-cjhj
- https://github.com/nextcloud/server/pull/56982
- https://hackerone.com/reports/3425534
- https://nvd.nist.gov/vuln/detail/CVE-2026-45810
