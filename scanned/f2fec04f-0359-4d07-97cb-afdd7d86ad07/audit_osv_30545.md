# [M] ARM: fix cacheflush with PAN

## Summary
Severity: Medium
Advisory: CVE-2024-53137
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53137
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: fix cacheflush with PAN

It seems that the cacheflush syscall got broken when PAN for LPAE was
implemented. User access was not enabled around the cache maintenance
instructions, causing them to fault.

## References
- https://git.kernel.org/stable/c/ca29cfcc4a21083d671522ad384532e28a43f033
- https://git.kernel.org/stable/c/e6960a2ed49c9a25357817535f7cc50594a58604
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53137.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53137
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
