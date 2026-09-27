# [M] phy: usb: sunplus: Fix potential null-ptr-deref in sp_usb_phy_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49756
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49756
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: usb: sunplus: Fix potential null-ptr-deref in sp_usb_phy_probe()

sp_usb_phy_probe() will call platform_get_resource_byname() that may fail
and return NULL. devm_ioremap() will use usbphy->moon4_res_mem->start as
input, which may causes null-ptr-deref. Check the ret value of
platform_get_resource_byname() to avoid the null-ptr-deref.

## References
- https://git.kernel.org/stable/c/17eee264ef386ef30a69dd70e36f29893b85c170
- https://git.kernel.org/stable/c/d838b5c99bcecd593b4710a93fce8fdbf122395b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49756.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49756
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
