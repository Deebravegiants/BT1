# [M] CVE-2021-41241

## Summary
Severity: Medium
Advisory: CVE-2021-41241
Aliases: GHSA-m4wp-r357-4q94
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-03-08
Source: https://osv.dev/vulnerability/CVE-2021-41241
Type: osv

## Details
Nextcloud server is a self hosted system designed to provide cloud style services. The groupfolders application for Nextcloud allows sharing a folder with a group of people. In addition, it allows setting "advanced permissions" on subfolders, for example, a user could be granted access to the groupfolder but not specific subfolders. Due to a lacking permission check in affected versions, a user could still access these subfolders by copying the groupfolder to another location. It is recommended that the Nextcloud Server is upgraded to 20.0.14, 21.0.6 or 22.2.1. Users unable to upgrade should disable the "groupfolders" application in the admin settings.

## References
- https://security.gentoo.org/glsa/202208-17
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-m4wp-r357-4q94
- https://github.com/nextcloud/groupfolders/issues/1692
- https://github.com/nextcloud/server/pull/29362
