# [H] CVE-2020-24742

## Summary
Severity: High
Advisory: CVE-2020-24742
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-09
Source: https://osv.dev/vulnerability/CVE-2020-24742
Type: osv

## Details
An issue has been fixed in Qt versions 5.14.0 where QPluginLoader attempts to load plugins relative to the working directory, allowing attackers to execute arbitrary code via crafted files.

## References
- https://codereview.qt-project.org/c/qt/qtbase/+/280730
