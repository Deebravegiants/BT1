# [H] CVE-2018-7421

## Summary
Severity: High
Advisory: CVE-2018-7421
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7421
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.12 and 2.4.0 to 2.4.4, the DMP dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-dmp.c by correctly supporting a bounded number of Security Categories for a DMP Security Classification.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=656812ee1f2a8ddfd383b02a066e888f5919e17a
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=e8be5adae469ba563acfad2c2b98673e1afaf901
- https://www.wireshark.org/security/wnpa-sec-2018-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14408
