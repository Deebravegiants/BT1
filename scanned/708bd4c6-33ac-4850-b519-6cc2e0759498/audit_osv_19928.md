# [M] CVE-2021-28039

## Summary
Severity: Medium
Advisory: CVE-2021-28039
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-03-05
Source: https://osv.dev/vulnerability/CVE-2021-28039
Type: osv

## Details
An issue was discovered in the Linux kernel 5.9.x through 5.11.3, as used with Xen. In some less-common configurations, an x86 PV guest OS user can crash a Dom0 or driver domain via a large amount of I/O activity. The issue relates to misuse of guest physical addresses when a configuration has CONFIG_XEN_UNPOPULATED_ALLOC but not CONFIG_XEN_BALLOON_MEMORY_HOTPLUG.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=882213990d32fd224340a4533f6318dd152be4b2
- https://security.netapp.com/advisory/ntap-20210409-0001/
- http://xenbits.xen.org/xsa/advisory-369.html
- http://www.openwall.com/lists/oss-security/2021/03/05/2
