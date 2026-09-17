# [M] bcache: revert replacing IS_ERR_OR_NULL with IS_ERR again

## Summary
Severity: Medium
Advisory: CVE-2024-48881
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-48881
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.5.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bcache: revert replacing IS_ERR_OR_NULL with IS_ERR again

Commit 028ddcac477b ("bcache: Remove unnecessary NULL point check in
node allocations") leads a NULL pointer deference in cache_set_flush().

1721         if (!IS_ERR_OR_NULL(c->root))
1722                 list_add(&c->root->list, &c->btree_cache);

>From the above code in cache_set_flush(), if previous registration code
fails before allocating c->root, it is possible c->root is NULL as what
it is initialized. __bch_btree_node_alloc() never returns NULL but
c->root is possible to be NULL at above line 1721.

This patch replaces IS_ERR() by IS_ERR_OR_NULL() to fix this.

## References
- https://git.kernel.org/stable/c/336e30f32ae7c043fde0f6fa21586ff30bea9fe2
- https://git.kernel.org/stable/c/4379c5828492a4c2a651c8f826a01453bd2b80b0
- https://git.kernel.org/stable/c/5202391970ffbf81975251b3526b890ba027b715
- https://git.kernel.org/stable/c/5e0e913624bcd24f3de414475018d3023f060ee1
- https://git.kernel.org/stable/c/b2e382ae12a63560fca35050498e19e760adf8c0
- https://git.kernel.org/stable/c/cc05aa2c0117e20fa25a3c0d915f98b8f2e78667
- https://git.kernel.org/stable/c/fb5fee35bdd18316a84b5f30881a24e1415e1464
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48881.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48881
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
