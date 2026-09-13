# [H] Nextcloud: Cross-Account Calendar Takeover via Unauthorized Group-Member-Set Update

## Summary
Severity: High
Advisory: BIT-nextcloud-2026-45281
Aliases: CVE-2026-45281, GHSA-hrrv-mp25-26vv
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2026-45281
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=33.0.0 <33.0.3

## Details
Nextcloud is an open source content collaboration platform. In Nextcloud Server from versions 32.0.0 to before 32.0.9, and 33.0.0 to before 33.0.3, with the knowledge of other users’ principal URL an attacker could possibly send a request to gain full access to their calendar. Therefore, the attacker must be an authenticated user. This is because of improper authorization controls in the backend of the calendar. If the attacker had access to the calendar, they would be able to view and modify it. It is recommended that the Nextcloud Server is upgraded to 33.0.3 or 32.0.9. It is recommended that the Nextcloud Enterprise Server is upgraded to 33.0.3, 32.0.9, 31.0.14.5, 30.0.17.9, 29.0.16.16, 28.0.14.17, 27.1.11.26, 26.0.13.26, 25.0.13.29, 24.0.12.34, 23.0.12.35, 22.2.10.39, or 21.0.9.23

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-hrrv-mp25-26vv
- https://github.com/nextcloud/server/pull/59962
- https://hackerone.com/reports/3545964
- https://nvd.nist.gov/vuln/detail/CVE-2026-45281
