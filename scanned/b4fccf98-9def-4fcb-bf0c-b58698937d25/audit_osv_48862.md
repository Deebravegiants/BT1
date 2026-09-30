# [H] CVE-2018-16554

## Summary
Severity: High
Advisory: CVE-2018-16554
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-16
Source: https://osv.dev/vulnerability/CVE-2018-16554
Type: osv

## Details
The ProcessGpsInfo function of the gpsinfo.c file of jhead 3.00 may allow a remote attacker to cause a denial-of-service attack or unspecified other impact via a malicious JPEG file, because of inconsistency between float and double in a sprintf format string during TAG_GPS_ALT handling.

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00037.html
- https://nimo-zhang.github.io/2018/09/07/bug-analysis-1/#more
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=908176
