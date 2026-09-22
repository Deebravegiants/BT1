# [M] MIPS: pgalloc: fix memory leak caused by pgd_free()

## Summary
Severity: Medium
Advisory: CVE-2022-49210
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49210
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

MIPS: pgalloc: fix memory leak caused by pgd_free()

pgd page is freed by generic implementation pgd_free() since commit
f9cb654cb550 ("asm-generic: pgalloc: provide generic pgd_free()"),
however, there are scenarios that the system uses more than one page as
the pgd table, in such cases the generic implementation pgd_free() won't
be applicable anymore. For example, when PAGE_SIZE_4KB is enabled and
MIPS_VA_BITS_48 is not enabled in a 64bit system, the macro "PGD_ORDER"
will be set as "1", which will cause allocating two pages as the pgd
table. Well, at the same time, the generic implementation pgd_free()
just free one pgd page, which will result in the memory leak.

The memory leak can be easily detected by executing shell command:
"while true; do ls > /dev/null; grep MemFree /proc/meminfo; done"

## References
- https://git.kernel.org/stable/c/1bf0d78c8cc3cf615a6e7bf33ada70b73592f0a1
- https://git.kernel.org/stable/c/2bc5bab9a763d520937e4f3fe8df51c6a1eceb97
- https://git.kernel.org/stable/c/5a8501d34b261906e4c76ec9da679f2cb4d309ed
- https://git.kernel.org/stable/c/d29cda15cab086d82d692de016f7249545d4b6b4
- https://git.kernel.org/stable/c/fa3d44424579972cc7c4fac3d9cf227798ebdfa0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49210.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49210
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
