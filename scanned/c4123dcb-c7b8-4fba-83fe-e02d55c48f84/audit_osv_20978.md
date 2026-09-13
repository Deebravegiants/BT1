# [M] CVE-2021-39224

## Summary
Severity: Medium
Advisory: CVE-2021-39224
Aliases: GHSA-56wm-r6jm-3v9h
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-39224
Type: osv

## Details
Nextcloud is an open-source, self-hosted productivity platform. The Nextcloud OfficeOnline application prior to version 1.1.1 returned verbatim exception messages to the user. This could result in a full path disclosure on shared files. (e.g. an attacker could see that the file `shared.txt` is located within `/files/$username/Myfolder/Mysubfolder/shared.txt`). It is recommended that the OfficeOnline application is upgraded to 1.1.1. As a workaround, one may disable the OfficeOnline application in the app settings.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-56wm-r6jm-3v9h
- https://github.com/nextcloud/officeonline/pull/204
