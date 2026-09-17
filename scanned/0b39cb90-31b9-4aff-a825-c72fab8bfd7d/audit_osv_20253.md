# [H] CVE-2021-32630

## Summary
Severity: High
Advisory: CVE-2021-32630
Aliases: GHSA-xpqj-67r8-25j2
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2021-32630
Type: osv

## Details
Admidio is a free, open source user management system for websites of organizations and groups. In Admidio before version 4.0.4, there is an authenticated RCE via .phar file upload. A php web shell can be uploaded via the Documents & Files upload feature. Someone with upload permissions could rename the php shell with a .phar extension, visit the file, triggering the payload for a reverse/bind shell. This can be mitigated by excluding a .phar file extension to be uploaded (like you did with .php .phtml .php5 etc). The vulnerability is patched in version 4.0.4.

## References
- https://github.com/Admidio/admidio/issues/994
- https://github.com/Admidio/admidio/releases/tag/v4.0.4
- https://github.com/Admidio/admidio/security/advisories/GHSA-xpqj-67r8-25j2
