# [M] Access to internal files of the Nextcloud Android app

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2022-39210
Aliases: CVE-2022-39210, GHSA-vw2w-gpcv-v39f
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2022-39210
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <3.21.0

## Details
Nextcloud android is the official Android client for the Nextcloud home server platform. Internal paths to the Nextcloud Android app files are not properly protected. As a result access to internal files of the from within the Nextcloud Android app is possible. This may lead to a leak of sensitive information in some cases. It is recommended that the Nextcloud Android app is upgraded to 3.21.0. There are no known workarounds for this issue.

## References
- https://github.com/nextcloud/android/pull/10544
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vw2w-gpcv-v39f
- https://nvd.nist.gov/vuln/detail/CVE-2022-39210
