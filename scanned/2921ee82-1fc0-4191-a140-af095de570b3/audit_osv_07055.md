# [M] Nextcloud: Two-Factor Authentication Bypass via Pending Session Token Replay

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2026-45690
Aliases: CVE-2026-45690, GHSA-jgcj-v42r-9922
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2026-45690
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=33.0.0 <33.0.3

## Details
Nextcloud is an open source content collaboration platform. In Nextcloud Server from versions 32.0.0 to before 32.0.9, and 33.0.0 to before 33.0.3, an authentication bypass vulnerability allowed attackers with knowledge of a user's password to circumvent two-factor authentication (2FA) protections. When a user initiated login with valid credentials on a 2FA-enabled account, the system created a temporary session token before enforcing the second factor challenge. This token could be extracted and replayed via HTTP Basic Authentication to gain unauthorized access to authenticated endpoints. It is recommended that the Nextcloud Server is upgraded to 33.0.3 or 32.0.9. It is recommended that the Nextcloud Enterprise Server is upgraded to 33.0.3, 32.0.9, 31.0.14.5, 30.0.17.9 or 29.0.16.16

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-jgcj-v42r-9922
- https://github.com/nextcloud/server/pull/59758
- https://hackerone.com/reports/3639301
- https://nvd.nist.gov/vuln/detail/CVE-2026-45690
