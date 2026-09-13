# [H] block: avoid to reuse `hctx` not removed from cpuhp callback list

## Summary
Severity: High
Advisory: CVE-2024-41149
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-41149
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.6 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: avoid to reuse `hctx` not removed from cpuhp callback list

If the 'hctx' isn't removed from cpuhp callback list, we can't reuse it,
otherwise use-after-free may be triggered.

## References
- https://git.kernel.org/stable/c/85672ca9ceeaa1dcf2777a7048af5f4aee3fd02b
- https://git.kernel.org/stable/c/b5792c162dcf6197bf3d2de2be6c8169435b73d0
- https://git.kernel.org/stable/c/ee18012c80155f6809522804099621070c69ec72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41149.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41149
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
