# [M] mm/huge_memory: Fix xarray node memory leak

## Summary
Severity: Medium
Advisory: CVE-2022-49334
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49334
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/huge_memory: Fix xarray node memory leak

If xas_split_alloc() fails to allocate the necessary nodes to complete the
xarray entry split, it sets the xa_state to -ENOMEM, which xas_nomem()
then interprets as "Please allocate more memory", not as "Please free
any unnecessary memory" (which was the intended outcome).  It's confusing
to use xas_nomem() to free memory in this context, so call xas_destroy()
instead.

## References
- https://git.kernel.org/stable/c/69a37a8ba1b408a1c7616494aa7018e4b3844cbe
- https://git.kernel.org/stable/c/95c8181b4947e000f3b9b8e5918d899fce77b93d
- https://git.kernel.org/stable/c/c0c84962e297927ba57fd6ddc2bb000c9d149655
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49334.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49334
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
