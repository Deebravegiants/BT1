# [H] CVE-2018-7330

## Summary
Severity: High
Advisory: CVE-2018-7330
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7330
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, epan/dissectors/packet-thread.c had an infinite loop that was addressed by using a correct integer data type.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=8ad0c5b3683a17d9e2e16bbf25869140fd5c1c66
- http://www.securityfocus.com/bid/103158
- https://www.wireshark.org/security/wnpa-sec-2018-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14428
