# [M] CVE-2019-18420

## Summary
Severity: Medium
Advisory: CVE-2019-18420
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/CVE-2019-18420
Type: osv

## Details
An issue was discovered in Xen through 4.12.x allowing x86 PV guest OS users to cause a denial of service via a VCPUOP_initialise hypercall. hypercall_create_continuation() is a variadic function which uses a printf-like format string to interpret its parameters. Error handling for a bad format character was done using BUG(), which crashes Xen. One path, via the VCPUOP_initialise hypercall, has a bad format character. The BUG() can be hit if VCPUOP_initialise executes for a sufficiently long period of time for a continuation to be created. Malicious guests may cause a hypervisor crash, resulting in a Denial of Service (DoS). Xen versions 4.6 and newer are vulnerable. Xen versions 4.5 and earlier are not vulnerable. Only x86 PV guests can exploit the vulnerability. HVM and PVH guests, and guests on ARM systems, cannot exploit the vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2BQKX7M2RHCWDBKNPX4KEBI3MJIH6AYZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I5WWPW4BSZDDW7VHU427XTVXV7ROOFFW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IZYATWNUGHRBG6I3TC24YHP5Y3J7I6KH/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00037.html
- https://security.gentoo.org/glsa/202003-56
- https://www.debian.org/security/2020/dsa-4602
- https://seclists.org/bugtraq/2020/Jan/21
- http://www.openwall.com/lists/oss-security/2019/10/31/1
- http://xenbits.xen.org/xsa/advisory-296.html
