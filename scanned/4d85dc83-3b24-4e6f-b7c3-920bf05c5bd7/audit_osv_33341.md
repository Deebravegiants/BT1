# [H] iommu/vt-d: debugfs: Fix legacy mode page table dump logic

## Summary
Severity: High
Advisory: CVE-2025-40155
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40155
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: debugfs: Fix legacy mode page table dump logic

In legacy mode, SSPTPTR is ignored if TT is not 00b or 01b. SSPTPTR
maybe uninitialized or zero in that case and may cause oops like:

 Oops: general protection fault, probably for non-canonical address
       0xf00087d3f000f000: 0000 [#1] SMP NOPTI
 CPU: 2 UID: 0 PID: 786 Comm: cat Not tainted 6.16.0 #191 PREEMPT(voluntary)
 Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.17.0-5.fc42 04/01/2014
 RIP: 0010:pgtable_walk_level+0x98/0x150
 RSP: 0018:ffffc90000f279c0 EFLAGS: 00010206
 RAX: 0000000040000000 RBX: ffffc90000f27ab0 RCX: 000000000000001e
 RDX: 0000000000000003 RSI: f00087d3f000f000 RDI: f00087d3f0010000
 RBP: ffffc90000f27a00 R08: ffffc90000f27a98 R09: 0000000000000002
 R10: 0000000000000000 R11: 0000000000000000 R12: f00087d3f000f000
 R13: 0000000000000000 R14: 0000000040000000 R15: ffffc90000f27a98
 FS:  0000764566dcb740(0000) GS:ffff8881f812c000(0000) knlGS:0000000000000000
 CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
 CR2: 0000764566d44000 CR3: 0000000109d81003 CR4: 0000000000772ef0
 PKRU: 55555554
 Call Trace:
  <TASK>
  pgtable_walk_level+0x88/0x150
  domain_translation_struct_show.isra.0+0x2d9/0x300
  dev_domain_translation_struct_show+0x20/0x40
  seq_read_iter+0x12d/0x490
...

Avoid walking the page table if TT is not 00b or 01b.

## References
- https://git.kernel.org/stable/c/d8cf7b59c49f9118fa875462e18686cb6b131bb5
- https://git.kernel.org/stable/c/df2bf759a0bdb71f13e327d7527260d09facc055
- https://git.kernel.org/stable/c/fbe6070c73badca726e4ff7877320e6c62339917
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40155.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40155
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
