# [H] audit: fix potential use-after-free in audit_del_rule()

## Summary
Severity: High
Advisory: CVE-2026-74512
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74512
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

audit: fix potential use-after-free in audit_del_rule()

`audit_del_rule()` destroys `e->rule.exe` via `audit_remove_mark_rule()`
before unlinking the rule from RCU-visible filter lists and waiting for a
grace period. Concurrent readers in `audit_filter()` and
`audit_filter_rules()` still dereference `e->rule.exe`, while the fsnotify
mark can be freed on an independent lifetime path. This creates a
use-after-free window during rule deletion.

Fix this by unlinking the rule from the RCU-visible lists and invoking
`synchronize_rcu()` before calling `audit_remove_mark_rule()` (and other
rule removal helpers). This ensures that all existing RCU readers have
exited the critical section before any underlying resources are destroyed.

## References
- https://git.kernel.org/stable/c/246df90b5f1a8a6e6abbd2f058b029558720adec
- https://git.kernel.org/stable/c/3f82927b399d7a276c0c12b6ff4424b747a0c9a7
- https://git.kernel.org/stable/c/45bf3df5b32e5a49953e7ceabc55f7dd85380e46
- https://git.kernel.org/stable/c/5b8f46864f06d6dbacb7dcea52bc084dfd122638
- https://git.kernel.org/stable/c/78bde7e9bd36eaae1b8e8cfcd47f12a34f301dbf
- https://git.kernel.org/stable/c/8ae135a8962be9d4e8a131eb18eb06cdf02a47ce
- https://git.kernel.org/stable/c/93616c567469510b7bba55b2674e0c4523fd7e64
- https://git.kernel.org/stable/c/cae0dfed5d307b240bff71c3cf206652d1b6f215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74512.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74512
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
