# [H] nommu: pass NULL argument to vma_iter_prealloc()

## Summary
Severity: High
Advisory: CVE-2024-53109
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53109
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nommu: pass NULL argument to vma_iter_prealloc()

When deleting a vma entry from a maple tree, it has to pass NULL to
vma_iter_prealloc() in order to calculate internal state of the tree, but
it passed a wrong argument.  As a result, nommu kernels crashed upon
accessing a vma iterator, such as acct_collect() reading the size of vma
entries after do_munmap().

This commit fixes this issue by passing a right argument to the
preallocation call.

## References
- https://git.kernel.org/stable/c/247d720b2c5d22f7281437fd6054a138256986ba
- https://git.kernel.org/stable/c/8bbf0ab631cdf1dade6745f137cff98751e6ced7
- https://git.kernel.org/stable/c/aceaf33b7666b72dfb86e0aa977be81e3bcbc727
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53109.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53109
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
