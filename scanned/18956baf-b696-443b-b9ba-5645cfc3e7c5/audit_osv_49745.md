# [H] CVE-2019-18421

## Summary
Severity: High
Advisory: CVE-2019-18421
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/CVE-2019-18421
Type: osv

## Details
An issue was discovered in Xen through 4.12.x allowing x86 PV guest OS users to gain host OS privileges by leveraging race conditions in pagetable promotion and demotion operations. There are issues with restartable PV type change operations. To avoid using shadow pagetables for PV guests, Xen exposes the actual hardware pagetables to the guest. In order to prevent the guest from modifying these page tables directly, Xen keeps track of how pages are used using a type system; pages must be "promoted" before being used as a pagetable, and "demoted" before being used for any other type. Xen also allows for "recursive" promotions: i.e., an operating system promoting a page to an L4 pagetable may end up causing pages to be promoted to L3s, which may in turn cause pages to be promoted to L2s, and so on. These operations may take an arbitrarily large amount of time, and so must be re-startable. Unfortunately, making recursive pagetable promotion and demotion operations restartable is incredibly complicated, and the code contains several races which, if triggered, can cause Xen to drop or retain extra type counts, potentially allowing guests to get write access to in-use pagetables. A malicious PV guest administrator may be able to escalate their privilege to that of the host. All x86 systems with untrusted PV guests are vulnerable. HVM and PVH guests cannot exercise this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I5WWPW4BSZDDW7VHU427XTVXV7ROOFFW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IZYATWNUGHRBG6I3TC24YHP5Y3J7I6KH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2BQKX7M2RHCWDBKNPX4KEBI3MJIH6AYZ/
- https://seclists.org/bugtraq/2020/Jan/21
- https://security.gentoo.org/glsa/202003-56
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00037.html
- https://www.debian.org/security/2020/dsa-4602
- http://xenbits.xen.org/xsa/advisory-299.html
- http://www.openwall.com/lists/oss-security/2019/10/31/3
