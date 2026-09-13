# [M] net: pds_core: Fix possible double free in error handling path

## Summary
Severity: Medium
Advisory: CVE-2024-26652
Ecosystem: Linux
CVSS: 4.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2024-26652
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.22, >=6.7.0 <6.7.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: pds_core: Fix possible double free in error handling path

When auxiliary_device_add() returns error and then calls
auxiliary_device_uninit(), Callback function pdsc_auxbus_dev_release
calls kfree(padev) to free memory. We shouldn't call kfree(padev)
again in the error handling path.

Fix this by cleaning up the redundant kfree() and putting
the error handling back to where the errors happened.

## References
- https://git.kernel.org/stable/c/995f802abff209514ac2ee03b96224237646cec3
- https://git.kernel.org/stable/c/ba18deddd6d502da71fd6b6143c53042271b82bd
- https://git.kernel.org/stable/c/ffda0e962f270b3ec937660afd15b685263232d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26652.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26652
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
