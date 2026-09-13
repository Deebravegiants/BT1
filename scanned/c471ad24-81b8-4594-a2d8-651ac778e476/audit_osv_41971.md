# [H] batman-adv: bla: fix report_work leak on backbone_gw purge

## Summary
Severity: High
Advisory: CVE-2026-64218
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64218
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: bla: fix report_work leak on backbone_gw purge

batadv_bla_purge_backbone_gw() removes stale backbone gateway entries,
but fails to properly handle their associated report_work:

- If report_work is running, the purge must wait for it to finish before
  freeing the backbone_gw, otherwise the worker may access freed memory
  (e.g. bat_priv).
- If report_work is pending, the purge must cancel it and release the
  reference held for that pending work item.

The previous implementation called hlist_for_each_entry_safe() inside a
spin_lock_bh() section, but cancel_work_sync() may sleep and therefore
cannot be called from within a spinlock-protected region.

Restructure the loop to handle one entry per spinlock critical section:
acquire the lock, find the next entry to purge, remove it from the hash
list, then release the lock before calling cancel_work_sync() and
dropping the hash_entry reference. Repeat until no more entries require
purging.

## References
- https://git.kernel.org/stable/c/0459430add32ea41f3e2ef9351610e6d33627a6b
- https://git.kernel.org/stable/c/3423a45e5c3d3c5129f88143a9a969787d7d5a0a
- https://git.kernel.org/stable/c/48663158222b3b7f6ee6791a67d512ede7fc94bb
- https://git.kernel.org/stable/c/95a7034661274cf5985708bd2f6d86ee46f88fa9
- https://git.kernel.org/stable/c/c6de1a5a9c406e30b91f1515a6ce05cc84023baa
- https://git.kernel.org/stable/c/ce2c0ee4d76d5ee4b391fe0e31334361e25030ec
- https://git.kernel.org/stable/c/eeddd7bab3d59c1e98642a204141f8c5d6194707
- https://git.kernel.org/stable/c/f1303adb1e59582f76c22798a2e2e150e054a9e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64218.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64218
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
