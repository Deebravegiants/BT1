# [H] CVE-2013-2120

## Summary
Severity: High
Advisory: CVE-2013-2120
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-11
Source: https://osv.dev/vulnerability/CVE-2013-2120
Type: osv

## Details
The %{password(...)} macro in pastemacroexpander.cpp in the KDE Paste Applet before 4.10.5 in kdeplasma-addons does not properly generate passwords, which allows context-dependent attackers to bypass authentication via a brute-force attack.

## References
- http://openwall.com/lists/oss-security/2013/05/28/5
- http://openwall.com/lists/oss-security/2013/05/29/6
- https://bugzilla.redhat.com/show_bug.cgi?id=969421
- https://projects.kde.org/projects/kde/kdeplasma-addons/repository/revisions/36a1fe49cb70f717c4a6e9eeee2c9186503a8dce
- http://openwall.com/lists/oss-security/2013/05/28/5
- http://openwall.com/lists/oss-security/2013/05/29/6
- https://projects.kde.org/projects/kde/kdeplasma-addons/repository/revisions/36a1fe49cb70f717c4a6e9eeee2c9186503a8dce
- http://openwall.com/lists/oss-security/2013/05/28/5
- http://openwall.com/lists/oss-security/2013/05/29/6
- https://bugzilla.redhat.com/show_bug.cgi?id=969421
- https://projects.kde.org/projects/kde/kdeplasma-addons/repository/revisions/36a1fe49cb70f717c4a6e9eeee2c9186503a8dce
- https://bugzilla.redhat.com/show_bug.cgi?id=969421
- http://archives.neohapsis.com/archives/bugtraq/2013-05/0114.html
