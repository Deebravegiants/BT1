# [H] dma-buf/dma-resv: check if the new fence is really later

## Summary
Severity: High
Advisory: CVE-2022-49935
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49935
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-buf/dma-resv: check if the new fence is really later

Previously when we added a fence to a dma_resv object we always
assumed the the newer than all the existing fences.

With Jason's work to add an UAPI to explicit export/import that's not
necessary the case any more. So without this check we would allow
userspace to force the kernel into an use after free error.

Since the change is very small and defensive it's probably a good
idea to backport this to stable kernels as well just in case others
are using the dma_resv object in the same way.

## References
- https://git.kernel.org/stable/c/a3f7c10a269d5b77dd5822ade822643ced3057f0
- https://git.kernel.org/stable/c/c4c798fe98adceb642050819cb57cbc8f5c27870
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49935.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49935
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
