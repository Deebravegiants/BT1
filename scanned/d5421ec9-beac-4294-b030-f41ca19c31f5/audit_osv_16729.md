# [M] CVE-2019-9209

## Summary
Severity: Medium
Advisory: CVE-2019-9209
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2019-9209
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.12 and 2.6.0 to 2.6.6, the ASN.1 BER and related dissectors could crash. This was addressed in epan/dissectors/packet-ber.c by preventing a buffer overflow associated with excessive digits in time values.

## References
- http://www.securityfocus.com/bid/107203
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=f8fbe9f934d65b2694fa74622e5eb2e1dc8cd20b
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00031.html
- https://seclists.org/bugtraq/2019/Mar/35
- https://usn.ubuntu.com/3986-1/
- https://www.debian.org/security/2019/dsa-4416
- https://www.wireshark.org/security/wnpa-sec-2019-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15447
