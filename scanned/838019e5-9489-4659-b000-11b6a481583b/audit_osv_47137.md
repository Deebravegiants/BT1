# [M] CVE-2015-9099

## Summary
Severity: Medium
Advisory: CVE-2015-9099
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-25
Source: https://osv.dev/vulnerability/CVE-2015-9099
Type: osv

## Details
The lame_init_params function in lame.c in libmp3lame.a in LAME 3.99.5 allows remote attackers to cause a denial of service (invalid read and application crash) via a crafted audio file with a negative sample rate.

## References
- http://www.securityfocus.com/bid/99279
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=775959
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=775959
