# [M] CVE-2020-25604

## Summary
Severity: Medium
Advisory: CVE-2020-25604
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/CVE-2020-25604
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. There is a race condition when migrating timers between x86 HVM vCPUs. When migrating timers of x86 HVM guests between its vCPUs, the locking model used allows for a second vCPU of the same guest (also operating on the timers) to release a lock that it didn't acquire. The most likely effect of the issue is a hang or crash of the hypervisor, i.e., a Denial of Service (DoS). All versions of Xen are affected. Only x86 systems are vulnerable. Arm systems are not vulnerable. Only x86 HVM guests can leverage the vulnerability. x86 PV and PVH cannot leverage the vulnerability. Only guests with more than one vCPU can exploit the vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4JRXMKEMQRQYWYEPHVBIWUEAVQ3LU4FN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DA633Y3G5KX7MKRN4PFEGM3IVTJMBEOM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJZERRBJN6E6STDCHT4JHP4MI6TKBCJE/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00008.html
- https://security.gentoo.org/glsa/202011-06
- https://www.debian.org/security/2020/dsa-4769
- https://xenbits.xen.org/xsa/advisory-336.html
