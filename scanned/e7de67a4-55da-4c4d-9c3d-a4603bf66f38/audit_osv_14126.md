# [H] CVE-2018-7328

## Summary
Severity: High
Advisory: CVE-2018-7328
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7328
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, epan/dissectors/packet-usb.c had an infinite loop that was addressed by rejecting short frame header lengths.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=69d09028c956f6e049145485ce9b3e2858789b2b
- http://www.securityfocus.com/bid/103158
- https://www.wireshark.org/security/wnpa-sec-2018-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14421
