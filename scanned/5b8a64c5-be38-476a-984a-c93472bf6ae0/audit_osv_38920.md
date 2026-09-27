# [C] dcache: Limit the minimal number of bucket to two

## Summary
Severity: Critical
Advisory: CVE-2026-43071
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-43071
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

dcache: Limit the minimal number of bucket to two

There is an OOB read problem on dentry_hashtable when user sets
'dhash_entries=1':
  BUG: unable to handle page fault for address: ffff888b30b774b0
  #PF: supervisor read access in kernel mode
  #PF: error_code(0x0000) - not-present page
  Oops: Oops: 0000 [#1] SMP PTI
  RIP: 0010:__d_lookup+0x56/0x120
   Call Trace:
    d_lookup.cold+0x16/0x5d
    lookup_dcache+0x27/0xf0
    lookup_one_qstr_excl+0x2a/0x180
    start_dirop+0x55/0xa0
    simple_start_creating+0x8d/0xa0
    debugfs_start_creating+0x8c/0x180
    debugfs_create_dir+0x1d/0x1c0
    pinctrl_init+0x6d/0x140
    do_one_initcall+0x6d/0x3d0
    kernel_init_freeable+0x39f/0x460
    kernel_init+0x2a/0x260

There will be only one bucket in dentry_hashtable when dhash_entries is
set as one, and d_hash_shift is calculated as 32 by dcache_init(). Then,
following process will access more than one buckets(which memory region
is not allocated) in dentry_hashtable:
 d_lookup
  b = d_hash(hash)
    dentry_hashtable + ((u32)hashlen >> d_hash_shift)
    // The C standard defines the behavior of right shift amounts
    // exceeding the bit width of the operand as undefined. The
    // result of '(u32)hashlen >> d_hash_shift' becomes 'hashlen',
    // so 'b' will point to an unallocated memory region.
  hlist_bl_for_each_entry_rcu(b)
   hlist_bl_first_rcu(head)
    h->first  // read OOB!

Fix it by limiting the minimal number of dentry_hashtable bucket to two,
so that 'd_hash_shift' won't exceeds the bit width of type u32.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/277cedabb0ab86baae83fa58218be13c6d3e5526
- https://git.kernel.org/stable/c/426ef05e82ee52c8d0e95fc0808b7383d8352d73
- https://git.kernel.org/stable/c/45b06bb5ea96f75ad81d7ef446f832ea6b0026fe
- https://git.kernel.org/stable/c/5718df131ab78897a9dd1f2e71c3ba732d4392af
- https://git.kernel.org/stable/c/755b40903eff563768d4d96fd4ef51ec48adde3b
- https://git.kernel.org/stable/c/ddd57ebce245f9c7e2f6902a6c087d6186d2385d
- https://git.kernel.org/stable/c/f08fe8891c3eeb63b73f9f1f6d97aa629c821579
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43071.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43071
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
