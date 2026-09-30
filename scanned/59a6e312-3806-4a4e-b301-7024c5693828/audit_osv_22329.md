# [H] CVE-2022-25255

## Summary
Severity: High
Advisory: CVE-2022-25255
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2022-25255
Type: osv

## Details
In Qt 5.9.x through 5.15.x before 5.15.9 and 6.x before 6.2.4 on Linux and UNIX, QProcess could execute a binary from the current working directory when not found in the PATH.

## References
- https://codereview.qt-project.org/c/qt/qtbase/+/393113
- https://codereview.qt-project.org/c/qt/qtbase/+/394914
- https://codereview.qt-project.org/c/qt/qtbase/+/396020
- https://download.qt.io/official_releases/qt/5.15/qprocess5-15.diff
- https://download.qt.io/official_releases/qt/6.2/qprocess6-2.diff
