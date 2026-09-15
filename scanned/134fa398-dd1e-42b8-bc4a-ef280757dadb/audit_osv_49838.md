# [M] CVE-2019-19582

## Summary
Severity: Medium
Advisory: CVE-2019-19582
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/CVE-2019-19582
Type: osv

## Details
An issue was discovered in Xen through 4.12.x allowing x86 guest OS users to cause a denial of service (infinite loop) because certain bit iteration is mishandled. In a number of places bitmaps are being used by the hypervisor to track certain state. Iteration over all bits involves functions which may misbehave in certain corner cases: On x86 accesses to bitmaps with a compile time known size of 64 may incur undefined behavior, which may in particular result in infinite loops. A malicious guest may cause a hypervisor crash or hang, resulting in a Denial of Service (DoS). All versions of Xen are vulnerable. x86 systems with 64 or more nodes are vulnerable (there might not be any such systems that Xen would run on). x86 systems with less than 64 nodes are not vulnerable.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/34HBFTYNMQMWIO2GGK7DB6KV4M6R5YPV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D5R73AYE53QA32KTMHUVKCX6E52CIS43/
- https://seclists.org/bugtraq/2020/Jan/21
- https://security.gentoo.org/glsa/202003-56
- https://www.debian.org/security/2020/dsa-4602
- https://xenbits.xen.org/xsa/advisory-307.html
