# [M] Malicious Android application can crash the Nextcloud Android Client

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2021-32694
Aliases: CVE-2021-32694, GHSA-h2gm-m374-99vc
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2021-32694
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <3.15.1

## Details
Nextcloud Android app is the Android client for Nextcloud. In versions prior to 3.15.1, a malicious application on the same device is possible to crash the Nextcloud Android Client due to an uncaught exception. The vulnerability is patched in version 3.15.1.

## References
- https://github.com/nextcloud/android/pull/7919
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-h2gm-m374-99vc
- https://hackerone.com/reports/859136
- https://nvd.nist.gov/vuln/detail/CVE-2021-32694
