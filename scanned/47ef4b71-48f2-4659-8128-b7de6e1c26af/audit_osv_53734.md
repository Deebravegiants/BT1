# [H] CVE-2023-2156

## Summary
Severity: High
Advisory: CVE-2023-2156
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-09
Source: https://osv.dev/vulnerability/CVE-2023-2156
Type: osv

## Details
A flaw was found in the networking subsystem of the Linux kernel within the handling of the RPL protocol. This issue results from the lack of proper handling of user-supplied data, which can lead to an assertion failure. This may allow an unauthenticated remote attacker to create a denial of service condition on the system.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00001.html
- https://security.netapp.com/advisory/ntap-20230622-0001/
- https://www.debian.org/security/2023/dsa-5453
- https://www.debian.org/security/2023/dsa-5448
- https://www.zerodayinitiative.com/advisories/ZDI-23-547/
- https://bugzilla.redhat.com/show_bug.cgi?id=2196292
- http://www.openwall.com/lists/oss-security/2023/05/17/8
- http://www.openwall.com/lists/oss-security/2023/05/18/1
- http://www.openwall.com/lists/oss-security/2023/05/19/1
- http://www.openwall.com/lists/oss-security/2023/05/17/9
