# [H] CVE-2016-7957

## Summary
Severity: High
Advisory: CVE-2016-7957
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2016-7957
Type: osv

## Details
In Wireshark 2.2.0, the Bluetooth L2CAP dissector could crash, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-btl2cap.c by avoiding use of a seven-byte memcmp for potentially shorter strings.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=355b56b1c6c545072ac0c1225730b526c6749f0a
- http://www.securityfocus.com/bid/97597
- https://www.wireshark.org/security/wnpa-sec-2016-56.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12825
