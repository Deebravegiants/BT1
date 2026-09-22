# [M] CVE-2017-9616

## Summary
Severity: Medium
Advisory: CVE-2017-9616
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-14
Source: https://osv.dev/vulnerability/CVE-2017-9616
Type: osv

## Details
In Wireshark 2.2.7, overly deep mp4 chunks may cause stack exhaustion (uncontrolled recursion) in the dissect_mp4_box function in epan/dissectors/file-mp4.c.

## References
- http://www.securityfocus.com/bid/99085
- http://www.securitytracker.com/id/1038706
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13777
