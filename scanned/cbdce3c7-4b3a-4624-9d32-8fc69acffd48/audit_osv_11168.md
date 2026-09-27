# [H] CVE-2017-6467

## Summary
Severity: High
Advisory: CVE-2017-6467
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-04
Source: https://osv.dev/vulnerability/CVE-2017-6467
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.4 and 2.0.0 to 2.0.10, there is a Netscaler file parser infinite loop, triggered by a malformed capture file. This was addressed in wiretap/netscaler.c by changing the restrictions on file size.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=284ad58d288722a8725401967bff0c4455488f0c
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/96561
- https://www.wireshark.org/security/wnpa-sec-2017-11.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12083
