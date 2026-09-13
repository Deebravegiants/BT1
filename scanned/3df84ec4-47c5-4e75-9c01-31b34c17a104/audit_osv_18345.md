# [M] CVE-2020-26260

## Summary
Severity: Medium
Advisory: CVE-2020-26260
Aliases: GHSA-8wfc-w2r5-x7cr
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26260
Type: osv

## Details
BookStack is a platform for storing and organising information and documentation. In BookStack before version 0.30.5, a user with permissions to edit a page could set certain image URL's to manipulate functionality in the exporting system, which would allow them to make server side requests and/or have access to a wider scope of files within the BookStack file storage locations. The issue was addressed in BookStack v0.30.5. As a workaround, page edit permissions could be limited to only those that are trusted until you can upgrade.

## References
- https://bookstackapp.com/blog/beta-release-v0-30-5/
- https://github.com/BookStackApp/BookStack/releases/tag/v0.30.5
- https://github.com/BookStackApp/BookStack/security/advisories/GHSA-8wfc-w2r5-x7cr
