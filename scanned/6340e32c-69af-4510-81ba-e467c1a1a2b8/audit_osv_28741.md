# [H] regmap: maple: Fix cache corruption in regcache_maple_drop()

## Summary
Severity: High
Advisory: CVE-2024-36019
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36019
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

regmap: maple: Fix cache corruption in regcache_maple_drop()

When keeping the upper end of a cache block entry, the entry[] array
must be indexed by the offset from the base register of the block,
i.e. max - mas.index.

The code was indexing entry[] by only the register address, leading
to an out-of-bounds access that copied some part of the kernel
memory over the cache contents.

This bug was not detected by the regmap KUnit test because it only
tests with a block of registers starting at 0, so mas.index == 0.

## References
- https://git.kernel.org/stable/c/00bb549d7d63a21532e76e4a334d7807a54d9f31
- https://git.kernel.org/stable/c/3af6c5ac72dc5b721058132a0a1d7779e443175e
- https://git.kernel.org/stable/c/51c4440b9d3fd7c8234e6de9170a487c03506e53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36019.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36019
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
