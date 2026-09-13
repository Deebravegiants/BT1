# [H] CVE-2020-26210

## Summary
Severity: High
Advisory: CVE-2020-26210
Aliases: GHSA-7p2j-4h6p-cq3h
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N)
Published: 2020-11-03
Source: https://osv.dev/vulnerability/CVE-2020-26210
Type: osv

## Details
In BookStack before version 0.30.4, a user with permissions to edit a page could add an attached link which would execute untrusted JavaScript code when clicked by a viewer of the page. Dangerous content may remain in the database after this update. If you think this could have been exploited the linked advisory provides a SQL query to test. As a workaround, page edit permissions could be limited to only those that are trusted until you can upgrade although this will not address existing exploitation of this vulnerability. The issue is fixed in version 0.30.4.

## References
- https://github.com/BookStackApp/BookStack/releases/tag/v0.30.4
- https://bookstackapp.com/blog/beta-release-v0-30-4/
- https://github.com/BookStackApp/BookStack/commit/349162ea139556b2d25e09e155cec84e21cc9227
- https://github.com/BookStackApp/BookStack/security/advisories/GHSA-7p2j-4h6p-cq3h
