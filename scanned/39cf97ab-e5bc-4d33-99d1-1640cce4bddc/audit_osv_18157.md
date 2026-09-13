# [M] CVE-2020-24619

## Summary
Severity: Medium
Advisory: CVE-2020-24619
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-09-22
Source: https://osv.dev/vulnerability/CVE-2020-24619
Type: osv

## Details
In mainwindow.cpp in Shotcut before 20.09.13, the upgrade check misuses TLS because of setPeerVerifyMode(QSslSocket::VerifyNone). A man-in-the-middle attacker could offer a spoofed download resource.

## References
- https://shotcut.org/blog/new-release-200913/
- https://github.com/mltframework/shotcut/commit/f008adc039642307f6ee3378d378cdb842e52c1d
