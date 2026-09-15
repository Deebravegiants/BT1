# [H] CVE-2018-9261

## Summary
Severity: High
Advisory: CVE-2018-9261
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9261
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.5 and 2.2.0 to 2.2.13, the NBAP dissector could crash with a large loop that ends with a heap-based buffer overflow. This was addressed in epan/dissectors/packet-nbap.c by prohibiting the self-linking of DCH-IDs.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=66bc372716e04d6a8afdf6712583c9b5d11fee55
- https://lists.debian.org/debian-lts-announce/2018/05/msg00019.html
- https://www.debian.org/security/2018/dsa-4217
- https://www.wireshark.org/security/wnpa-sec-2018-18.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14471
