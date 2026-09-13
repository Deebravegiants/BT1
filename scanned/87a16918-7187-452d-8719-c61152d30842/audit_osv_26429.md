# [H] ipv6/addrconf: fix a potential refcount underflow for idev

## Summary
Severity: High
Advisory: CVE-2023-53189
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53189
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6/addrconf: fix a potential refcount underflow for idev

Now in addrconf_mod_rs_timer(), reference idev depends on whether
rs_timer is not pending. Then modify rs_timer timeout.

There is a time gap in [1], during which if the pending rs_timer
becomes not pending. It will miss to hold idev, but the rs_timer
is activated. Thus rs_timer callback function addrconf_rs_timer()
will be executed and put idev later without holding idev. A refcount
underflow issue for idev can be caused by this.

	if (!timer_pending(&idev->rs_timer))
		in6_dev_hold(idev);
		  <--------------[1]
	mod_timer(&idev->rs_timer, jiffies + when);

To fix the issue, hold idev if mod_timer() return 0.

## References
- https://git.kernel.org/stable/c/06a0716949c22e2aefb648526580671197151acc
- https://git.kernel.org/stable/c/1f656e483eb4733d62f18dfb206a49b78f60f495
- https://git.kernel.org/stable/c/2ad31ce40e8182860b631e37209e93e543790b7c
- https://git.kernel.org/stable/c/436b7cc7eae7851c184b671ed7a4a64c750b86f7
- https://git.kernel.org/stable/c/82abd1c37d3bf2a2658b34772c17a25a6f9cca42
- https://git.kernel.org/stable/c/c6395e32935d35e6f935e7caf1c2dac5a95943b4
- https://git.kernel.org/stable/c/c7eeba47058532f6077d6a658e38b6698f6ae71a
- https://git.kernel.org/stable/c/df62fdcd004afa72ecbed0e862ebb983acd3aa57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53189.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53189
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
