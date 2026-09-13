# [H] CVE-2017-6474

## Summary
Severity: High
Advisory: CVE-2017-6474
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-04
Source: https://osv.dev/vulnerability/CVE-2017-6474
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.4 and 2.0.0 to 2.0.10, there is a NetScaler file parser infinite loop, triggered by a malformed capture file. This was addressed in wiretap/netscaler.c by validating record sizes.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=a998c9195f183d85f5b0bbeebba21a2d4d303d47
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/96566
- https://www.wireshark.org/security/wnpa-sec-2017-07.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13429
