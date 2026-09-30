# [C] CVE-2017-16844

## Summary
Severity: Critical
Advisory: CVE-2017-16844
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-16
Source: https://osv.dev/vulnerability/CVE-2017-16844
Type: osv

## Details
Heap-based buffer overflow in the loadbuf function in formisc.c in formail in procmail 3.22 allows remote attackers to cause a denial of service (application crash) or possibly execute arbitrary code via a crafted e-mail message because of a hardcoded realloc size, a different vulnerability than CVE-2014-3618.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00019.html
- https://www.debian.org/security/2017/dsa-4041
- http://www.securitytracker.com/id/1039844
- https://access.redhat.com/errata/RHSA-2017:3269
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=876511
