# [M] CVE-2021-32766

## Summary
Severity: Medium
Advisory: CVE-2021-32766
Aliases: GHSA-gcf3-3wmc-88jr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-32766
Type: osv

## Details
Nextcloud Text is an open source plaintext editing application which ships with the nextcloud server. In affected versions the Nextcloud Text application returned different error messages depending on whether a folder existed in a public link share. This is problematic in case the public link share has been created with "Upload Only" privileges. (aka "File Drop"). A link share recipient is not expected to see which folders or files exist in a "File Drop" share. Using this vulnerability an attacker is able to enumerate folders in such a share. Exploitation requires that the attacker has access to a valid affected "File Drop" link share. It is recommended that the Nextcloud Server is upgraded to 20.0.12, 21.0.4 or 22.0.1. Users who are unable to upgrade are advised to disable the Nextcloud Text application in the app settings.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-gcf3-3wmc-88jr
- https://hackerone.com/reports/1253475
- https://github.com/nextcloud/text/pull/1716
