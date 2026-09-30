# [M] Permission bypass in Nextcloud Android App

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2021-41166
Aliases: CVE-2021-41166, GHSA-wrwg-jwpg-r3c4
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2021-41166
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <3.17.1

## Details
The Nextcloud Android app is the Android client for Nextcloud, a self-hosted productivity platform. An issue in versions prior to 3.17.1 may lead to sensitive information disclosure. An unauthorized app that does not have the otherwise required `MANAGE_DOCUMENTS` permission may view image thumbnails for images it does not have permission to view. Version 3.17.1 contains a patch. There are no known workarounds.

## References
- https://github.com/nextcloud/android/commit/aa47197109970b8449c4e44601eba36e3481b086
- https://github.com/nextcloud/android/commit/b6ecf515b38c2d82d32743f27236534f3e03ee0c
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wrwg-jwpg-r3c4
- https://hackerone.com/reports/1358597
- https://nvd.nist.gov/vuln/detail/CVE-2021-41166
