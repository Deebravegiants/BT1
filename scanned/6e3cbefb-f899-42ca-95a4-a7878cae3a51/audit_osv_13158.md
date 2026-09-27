# [H] CVE-2018-18226

## Summary
Severity: High
Advisory: CVE-2018-18226
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-12
Source: https://osv.dev/vulnerability/CVE-2018-18226
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.3, the Steam IHS Discovery dissector could consume system memory. This was addressed in epan/dissectors/packet-steam-ihs-discovery.c by changing the memory-management approach.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6e920ddc3cad2886ef07ca1a8e50e2a5c50986f7
- http://www.securityfocus.com/bid/105583
- http://www.securitytracker.com/id/1041909
- https://www.debian.org/security/2018/dsa-4359
- https://www.wireshark.org/security/wnpa-sec-2018-48.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15171
