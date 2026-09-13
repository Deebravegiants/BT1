# [M] App pin of the iOS app can be bypassed in Nextcloud iOS

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2023-28647
Aliases: CVE-2023-28647, GHSA-wjgg-2v4p-2gq6
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2023-28647
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <4.7.0

## Details
Nextcloud iOS is an ios application used to interface with the nextcloud home cloud ecosystem. In versions prior to 4.7.0 when an attacker has physical access to an unlocked device, they may enable the integration into the iOS Files app and bypass the Nextcloud pin/password protection and gain access to a users files. It is recommended that the Nextcloud iOS app is upgraded to 4.7.0. There are no known workarounds for this vulnerability.

## References
- https://github.com/nextcloud/ios/pull/2344
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wjgg-2v4p-2gq6
- https://nvd.nist.gov/vuln/detail/CVE-2023-28647
