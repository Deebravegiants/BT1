# [M] CVE-2020-17498

## Summary
Severity: Medium
Advisory: CVE-2020-17498
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-17498
Type: osv

## Details
In Wireshark 3.2.0 to 3.2.5, the Kafka protocol dissector could crash. This was addressed in epan/dissectors/packet-kafka.c by avoiding a double free during LZ4 decompression.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=76afda963de4f0b9be24f2d8e873990a5cbf221b
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AII7UYDPNKYE75AZL45M6HAV2COP7F6S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G7LO7DAPN33FL4JQ7DDPB76SIEFGMZSQ/
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00038.html
- https://security.gentoo.org/glsa/202008-14
- https://www.wireshark.org/security/wnpa-sec-2020-10.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=16672
- https://www.oracle.com/security-alerts/cpujan2021.html
