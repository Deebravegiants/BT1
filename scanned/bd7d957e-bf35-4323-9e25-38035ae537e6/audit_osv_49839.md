# [H] CVE-2019-19583

## Summary
Severity: High
Advisory: CVE-2019-19583
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/CVE-2019-19583
Type: osv

## Details
An issue was discovered in Xen through 4.12.x allowing x86 HVM/PVH guest OS users to cause a denial of service (guest OS crash) because VMX VMEntry checks mishandle a certain case. Please see XSA-260 for background on the MovSS shadow. Please see XSA-156 for background on the need for #DB interception. The VMX VMEntry checks do not like the exact combination of state which occurs when #DB in intercepted, Single Stepping is active, and blocked by STI/MovSS is active, despite this being a legitimate state to be in. The resulting VMEntry failure is fatal to the guest. HVM/PVH guest userspace code may be able to crash the guest, resulting in a guest Denial of Service. All versions of Xen are affected. Only systems supporting VMX hardware virtual extensions (Intel, Cyrix, or Zhaoxin CPUs) are affected. Arm and AMD systems are unaffected. Only HVM/PVH guests are affected. PV guests cannot leverage the vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/34HBFTYNMQMWIO2GGK7DB6KV4M6R5YPV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D5R73AYE53QA32KTMHUVKCX6E52CIS43/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00011.html
- https://seclists.org/bugtraq/2020/Jan/21
- https://security.gentoo.org/glsa/202003-56
- https://www.debian.org/security/2020/dsa-4602
- https://xenbits.xen.org/xsa/advisory-308.html
