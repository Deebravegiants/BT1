# [M] CVE-2019-5719

## Summary
Severity: Medium
Advisory: CVE-2019-5719
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-08
Source: https://osv.dev/vulnerability/CVE-2019-5719
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.5 and 2.4.0 to 2.4.11, the ISAKMP dissector could crash. This was addressed in epan/dissectors/packet-isakmp.c by properly handling the case of a missing decryption data block.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=b5b02f2a9b8772d8814096f86c60a32889d61f2c
- https://lists.debian.org/debian-lts-announce/2019/01/msg00022.html
- https://seclists.org/bugtraq/2019/Mar/35
- https://www.debian.org/security/2019/dsa-4416
- https://www.wireshark.org/security/wnpa-sec-2019-04.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15374
