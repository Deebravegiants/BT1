# [H] KVM: arm64: Fix uninitialized memcache pointer in user_mem_abort()

## Summary
Severity: High
Advisory: CVE-2025-37996
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2025-37996
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Fix uninitialized memcache pointer in user_mem_abort()

Commit fce886a60207 ("KVM: arm64: Plumb the pKVM MMU in KVM") made the
initialization of the local memcache variable in user_mem_abort()
conditional, leaving a codepath where it is used uninitialized via
kvm_pgtable_stage2_map().

This can fail on any path that requires a stage-2 allocation
without transition via a permission fault or dirty logging.

Fix this by making sure that memcache is always valid.

## References
- https://git.kernel.org/stable/c/157dbc4a321f5bb6f8b6c724d12ba720a90f1a7c
- https://git.kernel.org/stable/c/a26d50f8a4a5049e956984797b5d0dedea4bbb18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37996.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37996
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
