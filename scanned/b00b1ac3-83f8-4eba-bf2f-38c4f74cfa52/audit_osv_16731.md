# [H] CVE-2019-9214

## Summary
Severity: High
Advisory: CVE-2019-9214
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2019-9214
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.12 and 2.6.0 to 2.6.6, the RPCAP dissector could crash. This was addressed in epan/dissectors/packet-rpcap.c by avoiding an attempted dereference of a NULL conversation.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=c557bb0910be271e49563756411a690a1bc53ce5
- https://usn.ubuntu.com/3986-1/
- http://www.securityfocus.com/bid/107203
- https://seclists.org/bugtraq/2019/Mar/35
- https://www.debian.org/security/2019/dsa-4416
- https://www.wireshark.org/security/wnpa-sec-2019-08.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15536
