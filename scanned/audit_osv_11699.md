# [H] CVE-2017-9348

## Summary
Severity: High
Advisory: CVE-2017-9348
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9348
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6, the DOF dissector could read past the end of a buffer. This was addressed in epan/dissectors/packet-dof.c by validating a size value.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=7fe55f96672b7bf2b4ceb9ae039a0f43eddd3151
- http://www.securityfocus.com/bid/98801
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-23.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1151
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13608
