# [H] CVE-2016-3890

## Summary
Severity: High
Advisory: CVE-2016-3890
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-11
Source: https://osv.dev/vulnerability/CVE-2016-3890
Type: osv

## Details
The Java Debug Wire Protocol (JDWP) implementation in adb/sockets.cpp in Android 4.x before 4.4.4, 5.0.x before 5.0.2, 5.1.x before 5.1.1, and 6.x before 2016-09-01 mishandles socket close operations, which allows attackers to gain privileges via a crafted application, aka internal bug 28347842.

## References
- http://www.securityfocus.com/bid/92851
- http://www.securitytracker.com/id/1036763
- http://source.android.com/security/bulletin/2016-09-01.html
- https://android.googlesource.com/platform/system/core/+/014b01706cc64dc9c2ad94a96f62e07c058d0b5d
- https://android.googlesource.com/platform/system/core/+/268068f25673242d1d5130d96202d3288c91b700
