# [M] CVE-2018-6790

## Summary
Severity: Medium
Advisory: CVE-2018-6790
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2018-6790
Type: osv

## Details
An issue was discovered in KDE Plasma Workspace before 5.12.0. dataengines/notifications/notificationsengine.cpp allows remote attackers to discover client IP addresses via a URL in a notification, as demonstrated by the src attribute of an IMG element.

## References
- https://access.redhat.com/errata/RHSA-2019:2141
- https://cgit.kde.org/plasma-workspace.git/commit/?id=5bc696b5abcdb460c1017592e80b2d7f6ed3107c
- https://cgit.kde.org/plasma-workspace.git/commit/?id=8164beac15ea34ec0d1564f0557fe3e742bdd938
- https://www.kde.org/announcements/plasma-5.11.5-5.12.0-changelog.php
- https://phabricator.kde.org/D10188
