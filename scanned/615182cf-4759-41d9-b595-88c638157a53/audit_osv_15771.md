# [H] CVE-2019-19553

## Summary
Severity: High
Advisory: CVE-2019-19553
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-05
Source: https://osv.dev/vulnerability/CVE-2019-19553
Type: osv

## Details
In Wireshark 3.0.0 to 3.0.6 and 2.6.0 to 2.6.12, the CMS dissector could crash. This was addressed in epan/dissectors/asn1/cms/packet-cms-template.c by ensuring that an object identifier is set to NULL after a ContentInfo dissection.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=34d2e0d5318d0a7e9889498c721639e5cbf4ce45
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.wireshark.org/security/wnpa-sec-2019-22.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15961
