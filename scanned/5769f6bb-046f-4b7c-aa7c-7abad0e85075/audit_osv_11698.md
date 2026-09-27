# [H] CVE-2017-9347

## Summary
Severity: High
Advisory: CVE-2017-9347
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9347
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6, the ROS dissector could crash with a NULL pointer dereference. This was addressed in epan/dissectors/asn1/ros/packet-ros-template.c by validating an OID.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=278e52f26e7e1a23f8d2e8ed98693328c992bdce
- http://www.securityfocus.com/bid/98800
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-31.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1216
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13637
- https://www.exploit-db.com/exploits/42124/
