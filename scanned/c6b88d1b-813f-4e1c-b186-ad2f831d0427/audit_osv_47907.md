# [H] CVE-2017-14520

## Summary
Severity: High
Advisory: CVE-2017-14520
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/CVE-2017-14520
Type: osv

## Details
In Poppler 0.59.0, a floating point exception occurs in Splash::scaleImageYuXd() in Splash.cc, which may lead to a potential attack when handling malicious PDF files.

## References
- https://www.debian.org/security/2018/dsa-4079
- https://bugs.freedesktop.org/show_bug.cgi?id=102719
