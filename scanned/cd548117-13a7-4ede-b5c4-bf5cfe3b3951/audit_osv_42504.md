# [H] net: mctp i3c: clean up notifier and buses if driver register fails

## Summary
Severity: High
Advisory: CVE-2026-68314
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68314
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mctp i3c: clean up notifier and buses if driver register fails

mctp_i3c_mod_init() registers the I3C bus notifier and then walks the
existing buses with i3c_for_each_bus_locked(mctp_i3c_bus_add_new, NULL)
before registering the I3C device driver.  If i3c_driver_register()
fails, the function returns the error directly, leaving the notifier
registered and every mctp_i3c_bus object created for the existing buses
allocated.  The notifier is left pointing into the module that failed to
load and the bus list is leaked.

Mirror the module exit path on this failure: unregister the notifier and
tear down the buses that were added before returning the error.

This issue was identified during our ongoing static-analysis research while
reviewing kernel code.

## References
- https://git.kernel.org/stable/c/03d1057305ef17ac3f5936ac1580bc9a1a826e14
- https://git.kernel.org/stable/c/49d15cfab247c0f60ce1800bdcd66850beea7b3a
- https://git.kernel.org/stable/c/a40e83a34eaa2be64372286040696f04eabcd09f
- https://git.kernel.org/stable/c/a8bd8c109da5a87f0c5db0c23cf550d039fde77c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68314.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68314
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
