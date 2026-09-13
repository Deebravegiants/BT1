# [M] CVE-2016-9373

## Summary
Severity: Medium
Advisory: CVE-2016-9373
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-17
Source: https://osv.dev/vulnerability/CVE-2016-9373
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.1 and 2.0.0 to 2.0.7, the DCERPC dissector could crash with a use-after-free, triggered by network traffic or a capture file. This was addressed in epan/dissectors/packet-dcerpc-nt.c and epan/dissectors/packet-dcerpc-spoolss.c by using the wmem file scope for private strings.

## References
- http://www.securitytracker.com/id/1037313
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=cc8e37f0f53c4401bb1644a34eddea345940a8df
- http://www.debian.org/security/2016/dsa-3719
- http://www.securityfocus.com/bid/94369
- https://www.wireshark.org/security/wnpa-sec-2016-61.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13072
