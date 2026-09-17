# [M] CVE-2019-18281

## Summary
Severity: Medium
Advisory: CVE-2019-18281
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-18281
Type: osv

## Details
An out-of-bounds memory access in the generateDirectionalRuns() function in qtextengine.cpp in Qt qtbase 5.11.x and 5.12.x before 5.12.5 allows attackers to cause a denial of service by crashing an application via a text file containing many directional characters.

## References
- https://usn.ubuntu.com/4275-1/
- https://seclists.org/bugtraq/2019/Nov/4
- https://security.gentoo.org/glsa/202003-60
- https://www.debian.org/security/2019/dsa-4556
- https://bugreports.qt.io/browse/QTBUG-77819
- https://bugs.launchpad.net/ubuntu/+source/qtbase-opensource-src/+bug/1848784
- https://codereview.qt-project.org/c/qt/qtbase/+/271889
