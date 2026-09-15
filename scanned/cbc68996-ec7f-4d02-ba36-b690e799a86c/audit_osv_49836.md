# [M] CVE-2019-19580

## Summary
Severity: Medium
Advisory: CVE-2019-19580
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/CVE-2019-19580
Type: osv

## Details
An issue was discovered in Xen through 4.12.x allowing x86 PV guest OS users to gain host OS privileges by leveraging race conditions in pagetable promotion and demotion operations, because of an incomplete fix for CVE-2019-18421. XSA-299 addressed several critical issues in restartable PV type change operations. Despite extensive testing and auditing, some corner cases were missed. A malicious PV guest administrator may be able to escalate their privilege to that of the host. All security-supported versions of Xen are vulnerable. Only x86 systems are affected. Arm systems are not affected. Only x86 PV guests can leverage the vulnerability. x86 HVM and PVH guests cannot leverage the vulnerability. Note that these attacks require very precise timing, which may be difficult to exploit in practice.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/34HBFTYNMQMWIO2GGK7DB6KV4M6R5YPV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D5R73AYE53QA32KTMHUVKCX6E52CIS43/
- https://seclists.org/bugtraq/2020/Jan/21
- https://security.gentoo.org/glsa/202003-56
- https://www.debian.org/security/2020/dsa-4602
- https://xenbits.xen.org/xsa/advisory-310.html
