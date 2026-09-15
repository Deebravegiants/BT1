# [H] x86/CPU/AMD: Add RDSEED fix for Zen5

## Summary
Severity: High
Advisory: CVE-2025-68313
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68313
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/CPU/AMD: Add RDSEED fix for Zen5

There's an issue with RDSEED's 16-bit and 32-bit register output
variants on Zen5 which return a random value of 0 "at a rate inconsistent
with randomness while incorrectly signaling success (CF=1)". Search the
web for AMD-SB-7055 for more detail.

Add a fix glue which checks microcode revisions.

  [ bp: Add microcode revisions checking, rewrite. ]

## References
- https://git.kernel.org/stable/c/36ff93e66d0efc46e39fab536a9feec968daa766
- https://git.kernel.org/stable/c/607b9fb2ce248cc5b633c5949e0153838992c152
- https://git.kernel.org/stable/c/e980de2ff109dacb6d9d3a77f01b27c467115ecb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68313.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68313
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
