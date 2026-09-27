# [H] CVE-2016-3100

## Summary
Severity: High
Advisory: CVE-2016-3100
CVSS: 8.4 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-13
Source: https://osv.dev/vulnerability/CVE-2016-3100
Type: osv

## Details
kinit in KDE Frameworks before 5.23.0 uses weak permissions (644) for /tmp/xauth-xxx-_y, which allows local users to obtain X11 cookies of other users and consequently capture keystrokes and possibly gain privileges by reading the file.

## References
- http://www.kde.com/announcements/kde-frameworks-5.23.0.php
- http://www.securityfocus.com/bid/91769
- https://bugs.kde.org/show_bug.cgi?id=358593
- https://bugs.kde.org/show_bug.cgi?id=363140
- https://quickgit.kde.org/?p=kinit.git&a=commitdiff&h=72f3702dbe6cf15c06dc13da2c99c864e9022a58
- https://quickgit.kde.org/?p=kinit.git&a=commitdiff&h=dece8fd89979cd1a86c03bcaceef6e9221e8d8cd
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00001.html
- https://www.kde.org/info/security/advisory-20160621-1.txt
