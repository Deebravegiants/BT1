# [H] Nextcloud user scoped external storage can be used to gather credentials of other users

## Summary
Severity: High
Advisory: CVE-2023-35928
Aliases: GHSA-637g-xp2c-qh5h
CVSS: 8.4 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-06-23
Source: https://osv.dev/vulnerability/CVE-2023-35928
Type: osv

## Details
Nextcloud Server is a space for data storage on Nextcloud, a self-hosted productivity playform. In NextCloud Server versions 25.0.0 until 25.0.7 and 26.0.0 until 26.0.2 and Nextcloud Enterprise Server versions 19.0.0 until 19.0.13.9, 20.0.0 until 20.0.14.14, 21.0.0 until 21.0.9.12, 22.0.0 until 22.2.10.12, 23.0.0 until 23.0.12.7, 24.0.0 until 24.0.12.2, 25.0.0 until 25.0.7, and 26.0.0 until 26.0.2, a user could use this functionality to get access to the login credentials of another user and take over their account. This issue has been patched in Nextcloud Server versions 25.0.7 and 26.0.2 and NextCloud Enterprise Server versions 19.0.13.9, 20.0.14.14, 21.0.9.12, 22.2.10.12, 23.0.12.7, 24.0.12.2, 25.0.7, and 26.0.2.

Three workarounds are available. Disable app files_external. Change config setting "Allow users to mount external storage" to disabled in "Administration" > "External storage" settings `…/index.php/settings/admin/externalstorages`. Change config setting to disallow users to create external storages in "Administration" > "External storage" settings `…/index.php/settings/admin/externalstorages` with the types FTP, Nextcloud, SFTP, and/or WebDAV.

## References
- https://hackerone.com/reports/1978882
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35928.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-637g-xp2c-qh5h
- https://nvd.nist.gov/vuln/detail/CVE-2023-35928
- https://github.com/nextcloud/server/pull/38265
