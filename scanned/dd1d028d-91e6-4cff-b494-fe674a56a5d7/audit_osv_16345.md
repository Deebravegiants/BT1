# [M] CVE-2019-5717

## Summary
Severity: Medium
Advisory: CVE-2019-5717
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-08
Source: https://osv.dev/vulnerability/CVE-2019-5717
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.5 and 2.4.0 to 2.4.11, the P_MUL dissector could crash. This was addressed in epan/dissectors/packet-p_mul.c by rejecting the invalid sequence number of zero.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=bf9272a92f3df1e4ccfaad434e123222ae5313f7
- http://www.securityfocus.com/bid/106482
- https://lists.debian.org/debian-lts-announce/2019/01/msg00022.html
- https://seclists.org/bugtraq/2019/Mar/35
- https://www.debian.org/security/2019/dsa-4416
- https://www.wireshark.org/security/wnpa-sec-2019-02.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15337
