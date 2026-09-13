# [H] CVE-2022-1158

## Summary
Severity: High
Advisory: CVE-2022-1158
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-05
Source: https://osv.dev/vulnerability/CVE-2022-1158
Type: osv

## Details
A flaw was found in KVM. When updating a guest's page table entry, vm_pgoff was improperly used as the offset to get the page's pfn. As vaddr and vm_pgoff are controllable by user-mode processes, this flaw allows unprivileged local users on the host to write outside the userspace region and potentially corrupt the kernel, resulting in a denial of service condition.

## References
- https://security.netapp.com/advisory/ntap-20230214-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2069793
- https://www.openwall.com/lists/oss-security/2022/04/08/4
