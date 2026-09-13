# [H] CVE-2020-15567

## Summary
Severity: High
Advisory: CVE-2020-15567
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/CVE-2020-15567
Type: osv

## Details
An issue was discovered in Xen through 4.13.x, allowing Intel guest OS users to gain privileges or cause a denial of service because of non-atomic modification of a live EPT PTE. When mapping guest EPT (nested paging) tables, Xen would in some circumstances use a series of non-atomic bitfield writes. Depending on the compiler version and optimisation flags, Xen might expose a dangerous partially written PTE to the hardware, which an attacker might be able to race to exploit. A guest administrator or perhaps even an unprivileged guest user might be able to cause denial of service, data corruption, or privilege escalation. Only systems using Intel CPUs are vulnerable. Systems using AMD CPUs, and Arm systems, are not vulnerable. Only systems using nested paging (hap, aka nested paging, aka in this case Intel EPT) are vulnerable. Only HVM and PVH guests can exploit the vulnerability. The presence and scope of the vulnerability depends on the precise optimisations performed by the compiler used to build Xen. If the compiler generates (a) a single 64-bit write, or (b) a series of read-modify-write operations in the same order as the source code, the hypervisor is not vulnerable. For example, in one test build using GCC 8.3 with normal settings, the compiler generated multiple (unlocked) read-modify-write operations in source-code order, which did not constitute a vulnerability. We have not been able to survey compilers; consequently we cannot say which compiler(s) might produce vulnerable code (with which code-generation options). The source code clearly violates the C rules, and thus should be considered vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MXESCOVI7AVRNC7HEAMFM7PMEO6D3AUH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VB3QJJZV23Z2IDYEMIHELWYSQBUEW6JP/
- https://www.debian.org/security/2020/dsa-4723
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00031.html
- http://www.openwall.com/lists/oss-security/2020/07/07/6
- https://security.gentoo.org/glsa/202007-02
- http://xenbits.xen.org/xsa/advisory-328.html
