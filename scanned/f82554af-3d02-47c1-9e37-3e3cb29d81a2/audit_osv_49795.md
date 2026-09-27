# [H] CVE-2019-19075

## Summary
Severity: High
Advisory: CVE-2019-19075
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19075
Type: osv

## Details
A memory leak in the ca8210_probe() function in drivers/net/ieee802154/ca8210.c in the Linux kernel before 5.3.8 allows attackers to cause a denial of service (memory consumption) by triggering ca8210_get_platform_data() failures, aka CID-6402939ec86e.

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4208-1/
- https://usn.ubuntu.com/4210-1/
- https://usn.ubuntu.com/4226-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.8
- https://github.com/torvalds/linux/commit/6402939ec86eaf226c8b8ae00ed983936b164908
