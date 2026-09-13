# [H] CVE-2019-10896

## Summary
Severity: High
Advisory: CVE-2019-10896
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-10896
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.13, 2.6.0 to 2.6.7, and 3.0.0, the DOF dissector could crash. This was addressed in epan/dissectors/packet-dof.c by properly handling generated IID and OID bytes.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=441b6d9071d6341e58dfe10719375489c5b8e3f0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4LYIOOQIMFQ3PA7AFBK4DNXHISTEYUC5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PU3QA2DUO3XS24QE24CQRP4A4XQQY76R/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- http://www.securityfocus.com/bid/107834
- https://lists.debian.org/debian-lts-announce/2020/10/msg00036.html
- https://usn.ubuntu.com/3986-1/
- https://www.wireshark.org/security/wnpa-sec-2019-15.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15617
