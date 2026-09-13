# [C] CVE-2013-1430

## Summary
Severity: Critical
Advisory: CVE-2013-1430
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-16
Source: https://osv.dev/vulnerability/CVE-2013-1430
Type: osv

## Details
An issue was discovered in xrdp before 0.9.1. When successfully logging in using RDP into an xrdp session, the file ~/.vnc/sesman_${username}_passwd is created. Its content is the equivalent of the user's cleartext password, DES encrypted with a known key.

## References
- https://security-tracker.debian.org/tracker/CVE-2013-1430
- https://github.com/neutrinolabs/xrdp/pull/497
- https://github.com/neutrinolabs/xrdp/pull/497
- https://security-tracker.debian.org/tracker/CVE-2013-1430
- http://www.securityfocus.com/bid/94958
