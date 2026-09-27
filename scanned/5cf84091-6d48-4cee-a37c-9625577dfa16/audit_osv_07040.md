# [M] Sensitive data may not be removed from storage on account removal

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2021-32658
Aliases: CVE-2021-32658, GHSA-g5gf-rmhm-wpxw
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2021-32658
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <3.16.1

## Details
Nextcloud Android is the Android client for the Nextcloud open source home cloud system. Due to a timeout issue the Android client may not properly clean all sensitive data on account removal. This could include sensitive key material such as the End-to-End encryption keys. It is recommended that the Nextcloud Android App is upgraded to 3.16.1

## References
- https://github.com/nextcloud/android/commit/355f3c745b464b741b20a3b96597303490c26333
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-g5gf-rmhm-wpxw
- https://hackerone.com/reports/1189168
- https://nvd.nist.gov/vuln/detail/CVE-2021-32658
