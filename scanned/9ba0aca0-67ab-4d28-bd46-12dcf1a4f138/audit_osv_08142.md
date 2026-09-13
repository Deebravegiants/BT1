# [H] CVE-2016-10700

## Summary
Severity: High
Advisory: CVE-2016-10700
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-24
Source: https://osv.dev/vulnerability/CVE-2016-10700
Type: osv

## Details
auth_login.php in Cacti before 1.0.0 allows remote authenticated users who use web authentication to bypass intended access restrictions by logging in as a user not in the cacti database, because the guest user is not considered. NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-2313.

## References
- http://bugs.cacti.net/view.php?id=2697
- http://www.cacti.net/release_notes_1_0_0.php
- https://web.archive.org/web/20160817090458/http://bugs.cacti.net/view.php?id=2697
- https://github.com/Cacti/cacti/commit/69983495cd41bf0903fe02baeef84b1fa85f2846
