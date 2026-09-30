# [H] VMCI: fix race between vmci_host_setup_notify and vmci_ctx_unset_notify

## Summary
Severity: High
Advisory: CVE-2025-38102
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38102
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

VMCI: fix race between vmci_host_setup_notify and vmci_ctx_unset_notify

During our test, it is found that a warning can be trigger in try_grab_folio
as follow:

  ------------[ cut here ]------------
  WARNING: CPU: 0 PID: 1678 at mm/gup.c:147 try_grab_folio+0x106/0x130
  Modules linked in:
  CPU: 0 UID: 0 PID: 1678 Comm: syz.3.31 Not tainted 6.15.0-rc5 #163 PREEMPT(undef)
  RIP: 0010:try_grab_folio+0x106/0x130
  Call Trace:
   <TASK>
   follow_huge_pmd+0x240/0x8e0
   follow_pmd_mask.constprop.0.isra.0+0x40b/0x5c0
   follow_pud_mask.constprop.0.isra.0+0x14a/0x170
   follow_page_mask+0x1c2/0x1f0
   __get_user_pages+0x176/0x950
   __gup_longterm_locked+0x15b/0x1060
   ? gup_fast+0x120/0x1f0
   gup_fast_fallback+0x17e/0x230
   get_user_pages_fast+0x5f/0x80
   vmci_host_unlocked_ioctl+0x21c/0xf80
  RIP: 0033:0x54d2cd
  ---[ end trace 0000000000000000 ]---

Digging into the source, context->notify_page may init by get_user_pages_fast
and can be seen in vmci_ctx_unset_notify which will try to put_page. However
get_user_pages_fast is not finished here and lead to following
try_grab_folio warning. The race condition is shown as follow:

cpu0			cpu1
vmci_host_do_set_notify
vmci_host_setup_notify
get_user_pages_fast(uva, 1, FOLL_WRITE, &context->notify_page);
lockless_pages_from_mm
gup_pgd_range
gup_huge_pmd  // update &context->notify_page
			vmci_host_do_set_notify
			vmci_ctx_unset_notify
			notify_page = context->notify_page;
			if (notify_page)
			put_page(notify_page);	// page is freed
__gup_longterm_locked
__get_user_pages
follow_trans_huge_pmd
try_grab_folio // warn here

To slove this, use local variable page to make notify_page can be seen
after finish get_user_pages_fast.

## References
- https://git.kernel.org/stable/c/00ddc7dad55b7bbb78df80d6e174d0c4764dea0c
- https://git.kernel.org/stable/c/1bd6406fb5f36c2bb1e96e27d4c3e9f4d09edde4
- https://git.kernel.org/stable/c/468aec888f838ce5174b96e0cb4396790d6f60ca
- https://git.kernel.org/stable/c/58a90db70aa6616411e5f69d1982d9b1dd97d774
- https://git.kernel.org/stable/c/6e3af836805ed1d7a699f76ec798626198917aa4
- https://git.kernel.org/stable/c/74095bbbb19ca74a0368d857603a2438c88ca86c
- https://git.kernel.org/stable/c/75b5313c80c39a26d27cbb602f968a05576c36f9
- https://git.kernel.org/stable/c/b4209e4b778e4e57d0636e1c9fc07a924dbc6043
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38102.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38102
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
