# [M] App lockout in nextcloud Android app can be bypassed via thirdparty apps

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2023-28646
Aliases: CVE-2023-28646, GHSA-c3rf-94h6-vj8v
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2023-28646
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=3.7.0 <3.24.1

## Details
Nextcloud android is an android app for interfacing with the nextcloud home server ecosystem. In versions from 3.7.0 and before 3.24.1 an attacker that has access to the unlocked physical device can bypass the Nextcloud Android Pin/passcode protection via a thirdparty app. This allows to see meta information like sharer, sharees and activity of files. It is recommended that the Nextcloud Android app is upgraded to 3.24.1. There are no known workarounds for this vulnerability.

## References
- https://github.com/nextcloud/android/pull/11242
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-c3rf-94h6-vj8v
- https://nvd.nist.gov/vuln/detail/CVE-2023-28646
