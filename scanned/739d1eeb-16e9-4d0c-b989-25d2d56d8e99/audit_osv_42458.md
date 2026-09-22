# [H] misc: nsm: pin the module while the device is open

## Summary
Severity: High
Advisory: CVE-2026-68178
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68178
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: nsm: pin the module while the device is open

misc_open() installs a misc driver's file operations with fops_get(),
which pins file_operations::owner before replacing the file's f_op.  The
NSM misc device leaves nsm_dev_fops.owner unset, so opening /dev/nsm does
not take a module reference on the nsm driver.

If the driver is built as a module, an open file descriptor can therefore
survive rmmod of the module that provides its ioctl callbacks.  A later
ioctl through that descriptor can call into unloaded module text.

Set nsm_dev_fops.owner to THIS_MODULE so the misc core holds the module
while any /dev/nsm file descriptor is open, matching the lifetime
expectation for the installed file operations.

## References
- https://git.kernel.org/stable/c/1996639f824ce9468395cdb7bcb8f467fa787e77
- https://git.kernel.org/stable/c/1da310b94504d42001e9c32c43c5dc105b777e5f
- https://git.kernel.org/stable/c/3b231f1e9990f4c21220d0a69733ce2105891ff9
- https://git.kernel.org/stable/c/9e9a82d00c3d10129fc310a7547b24a679d5d920
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68178.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68178
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
