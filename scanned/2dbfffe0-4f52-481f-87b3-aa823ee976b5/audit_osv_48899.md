# [M] CVE-2018-17977

## Summary
Severity: Medium
Advisory: CVE-2018-17977
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-08
Source: https://osv.dev/vulnerability/CVE-2018-17977
Type: osv

## Details
The Linux kernel 4.14.67 mishandles certain interaction among XFRM Netlink messages, IPPROTO_AH packets, and IPPROTO_IP packets, which allows local users to cause a denial of service (memory consumption and system hang) by leveraging root access to execute crafted applications, as demonstrated on CentOS 7.

## References
- http://www.securityfocus.com/bid/105539
- https://www.openwall.com/lists/oss-security/2018/10/05/5
