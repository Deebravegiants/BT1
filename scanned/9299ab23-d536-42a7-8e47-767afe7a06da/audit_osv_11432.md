# [H] CVE-2017-7745

## Summary
Severity: High
Advisory: CVE-2017-7745
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7745
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the SIGCOMP dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-sigcomp.c by correcting a memory-size check.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=acd8e1a9b17ad274bea1e01e10e4481508a1cbf0
- http://www.securityfocus.com/bid/97627
- https://www.wireshark.org/security/wnpa-sec-2017-20.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13578
