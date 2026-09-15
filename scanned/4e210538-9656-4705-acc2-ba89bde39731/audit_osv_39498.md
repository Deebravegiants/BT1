# [H] crypto: ccp - Fix a crash due to incorrect cleanup usage of kfree

## Summary
Severity: High
Advisory: CVE-2026-45959
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45959
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: ccp - Fix a crash due to incorrect cleanup usage of kfree

Annotating a local pointer variable, which will be assigned with the
kmalloc-family functions, with the `__cleanup(kfree)` attribute will
make the address of the local variable, rather than the address returned
by kmalloc, passed to kfree directly and lead to a crash due to invalid
deallocation of stack address. According to other places in the repo,
the correct usage should be `__free(kfree)`. The code coincidentally
compiled because the parameter type `void *` of kfree is compatible with
the desired type `struct { ... } **`.

## References
- https://git.kernel.org/stable/c/90f9090e3e744a8fe3bb6fa0e61f577347728b0b
- https://git.kernel.org/stable/c/9a3ace9b010ffd8c422c97844ae152f7c53d6b18
- https://git.kernel.org/stable/c/d5abcc33ee76bc26d58b39dc1a097e43a99dd438
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45959.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45959
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
