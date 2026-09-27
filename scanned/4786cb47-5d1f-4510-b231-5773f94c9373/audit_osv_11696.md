# [H] CVE-2017-9345

## Summary
Severity: High
Advisory: CVE-2017-9345
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9345
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the DNS dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-dns.c by trying to detect self-referencing pointers.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=e280c9b637327a65d132bfe72d917b87e6844eb5
- http://www.securityfocus.com/bid/98798
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-26.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1206
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13633
