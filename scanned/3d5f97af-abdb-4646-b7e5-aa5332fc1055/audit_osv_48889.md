# [H] CVE-2018-17088

## Summary
Severity: High
Advisory: CVE-2018-17088
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-16
Source: https://osv.dev/vulnerability/CVE-2018-17088
Type: osv

## Details
The ProcessGpsInfo function of the gpsinfo.c file of jhead 3.00 may allow a remote attacker to cause a denial-of-service attack or unspecified other impact via a malicious JPEG file, because there is an integer overflow during a check for whether a location exceeds the EXIF data length. This is analogous to the CVE-2016-3822 integer overflow in exif.c. This gpsinfo.c vulnerability is unrelated to the CVE-2018-16554 gpsinfo.c vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00037.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=907925
