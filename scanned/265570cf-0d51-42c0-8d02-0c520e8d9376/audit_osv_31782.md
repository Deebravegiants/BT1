# [M] ptp: vmclock: Add .owner to vmclock_miscdev_fops

## Summary
Severity: Medium
Advisory: CVE-2025-21769
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21769
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptp: vmclock: Add .owner to vmclock_miscdev_fops

Without the .owner field, the module can be unloaded while /dev/vmclock0
is open, leading to an oops.

## References
- https://git.kernel.org/stable/c/3b5709225b43ee33e1026dd1fc0949a7f19b5289
- https://git.kernel.org/stable/c/7b07b040257c1b658ef3eca86e4b6ae02d65069c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21769.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21769
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
