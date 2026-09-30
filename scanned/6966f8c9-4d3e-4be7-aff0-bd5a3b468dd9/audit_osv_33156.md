# [H] efivarfs: Fix slab-out-of-bounds in efivarfs_d_compare

## Summary
Severity: High
Advisory: CVE-2025-39817
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39817
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.4.298, >=5.5.0 <5.10.242, >=5.11.0 <5.15.191, >=5.16.0 <6.1.150, >=6.2.0 <6.6.104, >=6.7.0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

efivarfs: Fix slab-out-of-bounds in efivarfs_d_compare

Observed on kernel 6.6 (present on master as well):

  BUG: KASAN: slab-out-of-bounds in memcmp+0x98/0xd0
  Call trace:
   kasan_check_range+0xe8/0x190
   __asan_loadN+0x1c/0x28
   memcmp+0x98/0xd0
   efivarfs_d_compare+0x68/0xd8
   __d_lookup_rcu_op_compare+0x178/0x218
   __d_lookup_rcu+0x1f8/0x228
   d_alloc_parallel+0x150/0x648
   lookup_open.isra.0+0x5f0/0x8d0
   open_last_lookups+0x264/0x828
   path_openat+0x130/0x3f8
   do_filp_open+0x114/0x248
   do_sys_openat2+0x340/0x3c0
   __arm64_sys_openat+0x120/0x1a0

If dentry->d_name.len < EFI_VARIABLE_GUID_LEN , 'guid' can become
negative, leadings to oob. The issue can be triggered by parallel
lookups using invalid filename:

  T1			T2
  lookup_open
   ->lookup
    simple_lookup
     d_add
     // invalid dentry is added to hash list

			lookup_open
			 d_alloc_parallel
			  __d_lookup_rcu
			   __d_lookup_rcu_op_compare
			    hlist_bl_for_each_entry_rcu
			    // invalid dentry can be retrieved
			     ->d_compare
			      efivarfs_d_compare
			      // oob

Fix it by checking 'guid' before cmp.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/0f63fbabeaaaaaaf5b742a2f4c1b4590d50bf1f6
- https://git.kernel.org/stable/c/568e7761279b99c6daa3002290fd6d8047ddb6d2
- https://git.kernel.org/stable/c/71581a82f38e5a4d807d71fc1bb59aead80ccf95
- https://git.kernel.org/stable/c/794399019301944fd6d2e0d7a51b3327e26c410e
- https://git.kernel.org/stable/c/925599eba46045930b850a98ae594d2e3028ac40
- https://git.kernel.org/stable/c/a6358f8cf64850f3f27857b8ed8c1b08cfc4685c
- https://git.kernel.org/stable/c/c2925cd6207079c3f4d040d082515db78d63afbf
- https://git.kernel.org/stable/c/d7f5e35e70507d10cbaff5f9e194ed54c4ee14f7
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39817.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39817
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
