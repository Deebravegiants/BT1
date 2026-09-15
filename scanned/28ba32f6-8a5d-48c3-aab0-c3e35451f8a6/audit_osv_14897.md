# [H] CVE-2019-12295

## Summary
Severity: High
Advisory: CVE-2019-12295
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-23
Source: https://osv.dev/vulnerability/CVE-2019-12295
Type: osv

## Details
In Wireshark 3.0.0 to 3.0.1, 2.6.0 to 2.6.8, and 2.4.0 to 2.4.14, the dissection engine could crash. This was addressed in epan/packet.c by restricting the number of layers and consequently limiting recursion.

## References
- http://www.securityfocus.com/bid/108464
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=7b6e197da4c497e229ed3ebf6952bae5c426a820
- https://support.f5.com/csp/article/K06725231?utm_source=f5support&amp%3Butm_medium=RSS
- https://lists.debian.org/debian-lts-announce/2020/10/msg00036.html
- https://support.f5.com/csp/article/K06725231
- https://usn.ubuntu.com/4133-1/
- https://www.wireshark.org/security/wnpa-sec-2019-19.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15778
