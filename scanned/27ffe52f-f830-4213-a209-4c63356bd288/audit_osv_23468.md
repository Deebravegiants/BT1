# [H] drm/vmwgfx: Remove rcu locks from user resources

## Summary
Severity: High
Advisory: CVE-2022-48887
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2022-48887
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <6.1.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Remove rcu locks from user resources

User resource lookups used rcu to avoid two extra atomics. Unfortunately
the rcu paths were buggy and it was easy to make the driver crash by
submitting command buffers from two different threads. Because the
lookups never show up in performance profiles replace them with a
regular spin lock which fixes the races in accesses to those shared
resources.

Fixes kernel oops'es in IGT's vmwgfx execution_buffer stress test and
seen crashes with apps using shared resources.

## References
- https://git.kernel.org/stable/c/7ac9578e45b20e3f3c0c8eb71f5417a499a7226a
- https://git.kernel.org/stable/c/a309c7194e8a2f8bd4539b9449917913f6c2cd50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48887.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
