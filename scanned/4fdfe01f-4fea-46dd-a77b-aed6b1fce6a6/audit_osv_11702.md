# [H] CVE-2017-9351

## Summary
Severity: High
Advisory: CVE-2017-9351
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9351
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the DHCP dissector could read past the end of a buffer. This was addressed in epan/dissectors/packet-bootp.c by extracting the Vendor Class Identifier more carefully.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=a6e033c14da13bd5f72dfe07a347586517639d12
- http://www.securityfocus.com/bid/98808
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-24.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1153
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1183
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13609
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13628
