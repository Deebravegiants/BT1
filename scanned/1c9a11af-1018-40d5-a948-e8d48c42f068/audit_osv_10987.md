# [C] CVE-2017-5545

## Summary
Severity: Critical
Advisory: CVE-2017-5545
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-01-21
Source: https://osv.dev/vulnerability/CVE-2017-5545
Type: osv

## Details
The main function in plistutil.c in libimobiledevice libplist through 1.12 allows attackers to obtain sensitive information from process memory or cause a denial of service (buffer over-read) via Apple Property List data that is too short.

## References
- https://lists.debian.org/debian-lts-announce/2020/04/msg00002.html
- http://www.securityfocus.com/bid/95702
- https://github.com/libimobiledevice/libplist/commit/7391a506352c009fe044dead7baad9e22dd279ee
- https://github.com/libimobiledevice/libplist/issues/87
