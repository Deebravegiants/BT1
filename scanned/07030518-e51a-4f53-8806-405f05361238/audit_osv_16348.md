# [M] CVE-2019-5721

## Summary
Severity: Medium
Advisory: CVE-2019-5721
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-08
Source: https://osv.dev/vulnerability/CVE-2019-5721
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.11, the ENIP dissector could crash. This was addressed in epan/dissectors/packet-enip.c by changing the memory-management approach so that a use-after-free is avoided.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=1c66174ec7aa19e2ddc79178cf59f15a654fc4fe
- https://www.wireshark.org/security/wnpa-sec-2019-05.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14470
