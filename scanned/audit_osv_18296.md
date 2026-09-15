# [H] CVE-2020-25863

## Summary
Severity: High
Advisory: CVE-2020-25863
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-25863
Type: osv

## Details
In Wireshark 3.2.0 to 3.2.6, 3.0.0 to 3.0.13, and 2.6.0 to 2.6.20, the MIME Multipart dissector could crash. This was addressed in epan/dissectors/packet-multipart.c by correcting the deallocation of invalid MIME parts.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4DQHPKZFQ7W3X34RYN3FWFYCFJD4FXJW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6IGRYKW4XLR44YDWTAH547ODYYBYPB2D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZUHMK5HYTUUDXA64T2TAMAFMYV674QBW/
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00038.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://gitlab.com/wireshark/wireshark/-/commit/5803c7b87b3414cdb8bf502af50bb406ca774482
- https://gitlab.com/wireshark/wireshark/-/issues/16741
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.wireshark.org/security/wnpa-sec-2020-11.html
