# [H] usb: phy: isp1301: fix non-OF device reference imbalance

## Summary
Severity: High
Advisory: CVE-2025-71145
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-71145
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: phy: isp1301: fix non-OF device reference imbalance

A recent change fixing a device reference leak in a UDC driver
introduced a potential use-after-free in the non-OF case as the
isp1301_get_client() helper only increases the reference count for the
returned I2C device in the OF case.

Increment the reference count also for non-OF so that the caller can
decrement it unconditionally.

Note that this is inherently racy just as using the returned I2C device
is since nothing is preventing the PHY driver from being unbound while
in use.

## References
- https://git.kernel.org/stable/c/03bbdaa4da8c6ea0c8431a5011db188a07822c8a
- https://git.kernel.org/stable/c/43e58abad6c08c5f0943594126ef4cd6559aac0b
- https://git.kernel.org/stable/c/5d3df03f70547d4e3fc10ed4381c052eff51b157
- https://git.kernel.org/stable/c/7501ecfe3e5202490c2d13dc7e181203601fcd69
- https://git.kernel.org/stable/c/75c5d9bce072abbbc09b701a49869ac23c34a906
- https://git.kernel.org/stable/c/b4b64fda4d30a83a7f00e92a0c8a1d47699609f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71145.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71145
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
