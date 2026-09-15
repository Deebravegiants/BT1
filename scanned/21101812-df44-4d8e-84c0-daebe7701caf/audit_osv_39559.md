# [H] fanotify: fix false positive on permission events

## Summary
Severity: High
Advisory: CVE-2026-46150
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46150
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

fanotify: fix false positive on permission events

fsnotify_get_mark_safe() may return false for a mark on an unrelated group,
which results in bypassing the permission check.

Fix by skipping over detached marks that are not in the current group.

## References
- https://git.kernel.org/stable/c/04bb66be92f48ed13c3faf1139d892df228789bc
- https://git.kernel.org/stable/c/4a7611ad653785fcdea5ff5f4441e2b7d05b7f11
- https://git.kernel.org/stable/c/7746e3bd4cc19b5092e00d32d676e329bfcb6900
- https://git.kernel.org/stable/c/7baa02b0ae9d17ec5f08836d8ea88ce1927d0678
- https://git.kernel.org/stable/c/895ebbedf88318607c24acc0f591c74b165e1d0a
- https://git.kernel.org/stable/c/a24765332e129c1916d5a6615418b75599b8fcdc
- https://git.kernel.org/stable/c/b7b24b28c8cd55844cab908f4f39dded638d5538
- https://git.kernel.org/stable/c/f130790f1acc8399f32652846c875a251efd040f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46150.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46150
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
