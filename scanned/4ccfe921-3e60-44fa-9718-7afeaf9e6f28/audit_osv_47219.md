# [H] CVE-2016-1233

## Summary
Severity: High
Advisory: CVE-2016-1233
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-01-26
Source: https://osv.dev/vulnerability/CVE-2016-1233
Type: osv

## Details
An unspecified udev rule in the Debian fuse package in jessie before 2.9.3-15+deb8u2, in stretch before 2.9.5-1, and in sid before 2.9.5-1 sets world-writable permissions for the /dev/cuse character device, which allows local users to gain privileges via a character device in /dev, related to an ioctl.

## References
- http://www.debian.org/security/2016/dsa-3451
