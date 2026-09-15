# [M] CVE-2017-9617

## Summary
Severity: Medium
Advisory: CVE-2017-9617
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-14
Source: https://osv.dev/vulnerability/CVE-2017-9617
Type: osv

## Details
In Wireshark 2.2.7, deeply nested DAAP data may cause stack exhaustion (uncontrolled recursion) in the dissect_daap_one_tag function in epan/dissectors/packet-daap.c in the DAAP dissector.

## References
- http://www.securityfocus.com/bid/99087
- http://www.securitytracker.com/id/1038706
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13799
