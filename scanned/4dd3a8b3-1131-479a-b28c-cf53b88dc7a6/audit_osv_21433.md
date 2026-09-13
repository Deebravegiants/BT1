# [C] CVE-2021-4301

## Summary
Severity: Critical
Advisory: CVE-2021-4301
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-07
Source: https://osv.dev/vulnerability/CVE-2021-4301
Type: osv

## Details
A vulnerability was found in slackero phpwcms up to 1.9.26 and classified as critical. Affected by this issue is some unknown functionality. The manipulation of the argument $phpwcms['db_prepend'] leads to sql injection. The attack may be launched remotely. Upgrading to version 1.9.27 is able to address this issue. The patch is identified as 77dafb6a8cc1015f0777daeb5792f43beef77a9d. It is recommended to upgrade the affected component. VDB-217418 is the identifier assigned to this vulnerability.

## References
- https://github.com/slackero/phpwcms/releases/tag/v1.9.27
- https://vuldb.com/?ctiid.217418
- https://vuldb.com/?id.217418
- https://github.com/slackero/phpwcms/commit/77dafb6a8cc1015f0777daeb5792f43beef77a9d
