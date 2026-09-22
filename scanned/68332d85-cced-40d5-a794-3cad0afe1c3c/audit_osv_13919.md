# [M] CVE-2018-5334

## Summary
Severity: Medium
Advisory: CVE-2018-5334
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-11
Source: https://osv.dev/vulnerability/CVE-2018-5334
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.3 and 2.2.0 to 2.2.11, the IxVeriWave file parser could crash. This was addressed in wiretap/vwr.c by correcting the signature timestamp bounds checks.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=dc308c05ba0673460fe80873b22d296880ee996d
- http://www.securityfocus.com/bid/102499
- https://lists.debian.org/debian-lts-announce/2018/01/msg00032.html
- https://www.debian.org/security/2018/dsa-4101
- https://www.wireshark.org/security/wnpa-sec-2018-03.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14297
