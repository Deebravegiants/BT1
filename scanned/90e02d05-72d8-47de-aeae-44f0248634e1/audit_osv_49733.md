# [M] CVE-2019-17351

## Summary
Severity: Medium
Advisory: CVE-2019-17351
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-10-08
Source: https://osv.dev/vulnerability/CVE-2019-17351
Type: osv

## Details
An issue was discovered in drivers/xen/balloon.c in the Linux kernel before 5.2.3, as used in Xen through 4.12.x, allowing guest OS users to cause a denial of service because of unrestricted resource consumption during the mapping of guest memory, aka CID-6ef36ab967c7.

## References
- https://usn.ubuntu.com/4286-1/
- https://usn.ubuntu.com/4286-2/
- http://www.openwall.com/lists/oss-security/2019/10/25/9
- https://xenbits.xen.org/xsa/advisory-300.html
- http://xenbits.xen.org/xsa/advisory-300.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.3
- https://security.netapp.com/advisory/ntap-20191031-0005/
- https://github.com/torvalds/linux/commit/6ef36ab967c71690ebe7e5ef997a8be4da3bc844
