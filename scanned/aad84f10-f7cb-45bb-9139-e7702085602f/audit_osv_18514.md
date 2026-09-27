# [H] CVE-2020-28030

## Summary
Severity: High
Advisory: CVE-2020-28030
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-02
Source: https://osv.dev/vulnerability/CVE-2020-28030
Type: osv

## Details
In Wireshark 3.2.0 to 3.2.7, the GQUIC dissector could crash. This was addressed in epan/dissectors/packet-gquic.c by correcting the implementation of offset advancement.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHZSVK7PO2LTGFQXFHFXY6SOMSQ7UPRS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V2667E6WKVE56G66BVBVD7LJPIDOJ7K3/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://www.wireshark.org/security/wnpa-sec-2020-15.html
- https://gitlab.com/wireshark/wireshark/-/issues/16887
- https://gitlab.com/wireshark/wireshark/-/commit/b287e7165e8aa89cde6ae37e7c257c5d87d16b9b
