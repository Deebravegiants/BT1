# [H] CVE-2016-3698

## Summary
Severity: High
Advisory: CVE-2016-3698
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-3698
Type: osv

## Details
libndp before 1.6, as used in NetworkManager, does not properly validate the origin of Neighbor Discovery Protocol (NDP) messages, which allows remote attackers to conduct man-in-the-middle attacks or cause a denial of service (network connectivity disruption) by advertising a node as a router from a non-local network.

## References
- http://www.openwall.com/lists/oss-security/2016/05/17/9
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.debian.org/security/2016/dsa-3581
- http://www.ubuntu.com/usn/USN-2980-1
- https://rhn.redhat.com/errata/RHSA-2016-1086.html
- https://github.com/jpirko/libndp/commit/2af9a55b38b55abbf05fd116ec097d4029115839
- https://github.com/jpirko/libndp/commit/a4892df306e0532487f1634ba6d4c6d4bb381c7f
