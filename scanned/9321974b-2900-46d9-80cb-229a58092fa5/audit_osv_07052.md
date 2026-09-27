# [M] Nextcloud: PIN bypass in PassCodeActivity via back button

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2026-45153
Aliases: CVE-2026-45153, GHSA-2w7v-5299-3hw5
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2026-45153
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=33.0.0 <33.1.0

## Details
Nextcloud is an open source content collaboration platform. From version 33.0.0 to before version 33.1.0, after unlocking a locked Android phone the back-button could be used to bypass the Nextcloud Files app PIN. This issue has been patched in version 33.1.0.

## References
- https://github.com/nextcloud/android/pull/16896
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-2w7v-5299-3hw5
- https://hackerone.com/reports/3625210
- https://nvd.nist.gov/vuln/detail/CVE-2026-45153
