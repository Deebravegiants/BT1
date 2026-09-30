# [H] CVE-2018-7419

## Summary
Severity: High
Advisory: CVE-2018-7419
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7419
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.12 and 2.4.0 to 2.4.4, the NBAP dissector could crash. This was addressed in epan/dissectors/asn1/nbap/nbap.cnf by ensuring DCH ID initialization.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=bebd3a1f50b0a27738d8d3da5b33c1b392eb7273
- http://www.securityfocus.com/bid/103159
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://www.debian.org/security/2018/dsa-4217
- https://www.wireshark.org/security/wnpa-sec-2018-14.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14443
