# [H] CVE-2018-19627

## Summary
Severity: High
Advisory: CVE-2018-19627
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19627
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.4 and 2.4.0 to 2.4.10, the IxVeriWave file parser could crash. This was addressed in wiretap/vwr.c by adjusting a buffer boundary.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=bdc33cfaecb1b4cf2c114ed9015713ddf8569a60
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.securityfocus.com/bid/106051
- https://www.debian.org/security/2018/dsa-4359
- https://www.wireshark.org/security/wnpa-sec-2018-55.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15279
- https://www.exploit-db.com/exploits/45951/
