# [M] rpcrdma: Always release the rpcrdma_device's xa_array

## Summary
Severity: Medium
Advisory: CVE-2024-53077
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53077
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

rpcrdma: Always release the rpcrdma_device's xa_array

Dai pointed out that the xa_init_flags() in rpcrdma_add_one() needs
to have a matching xa_destroy() in rpcrdma_remove_one() to release
underlying memory that the xarray might have accrued during
operation.

## References
- https://git.kernel.org/stable/c/36b7f5a4f300d038270324640ff7c1399245159d
- https://git.kernel.org/stable/c/63a81588cd2025e75fbaf30b65930b76825c456f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53077.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53077
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
