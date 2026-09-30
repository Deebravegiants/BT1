# [H] net/sched: act_ife: Fix metalist update behavior

## Summary
Severity: High
Advisory: CVE-2026-23378
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23378
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_ife: Fix metalist update behavior

Whenever an ife action replace changes the metalist, instead of
replacing the old data on the metalist, the current ife code is appending
the new metadata. Aside from being innapropriate behavior, this may lead
to an unbounded addition of metadata to the metalist which might cause an
out of bounds error when running the encode op:

[  138.423369][    C1] ==================================================================
[  138.424317][    C1] BUG: KASAN: slab-out-of-bounds in ife_tlv_meta_encode (net/ife/ife.c:168)
[  138.424906][    C1] Write of size 4 at addr ffff8880077f4ffe by task ife_out_out_bou/255
[  138.425778][    C1] CPU: 1 UID: 0 PID: 255 Comm: ife_out_out_bou Not tainted 7.0.0-rc1-00169-gfbdfa8da05b6 #624 PREEMPT(full)
[  138.425795][    C1] Hardware name: Bochs Bochs, BIOS Bochs 01/01/2011
[  138.425800][    C1] Call Trace:
[  138.425804][    C1]  <IRQ>
[  138.425808][    C1]  dump_stack_lvl (lib/dump_stack.c:122)
[  138.425828][    C1]  print_report (mm/kasan/report.c:379 mm/kasan/report.c:482)
[  138.425839][    C1]  ? srso_alias_return_thunk (arch/x86/lib/retpoline.S:221)
[  138.425844][    C1]  ? __virt_addr_valid (./arch/x86/include/asm/preempt.h:95 (discriminator 1) ./include/linux/rcupdate.h:975 (discriminator 1) ./include/linux/mmzone.h:2207 (discriminator 1) arch/x86/mm/physaddr.c:54 (discriminator 1))
[  138.425853][    C1]  ? ife_tlv_meta_encode (net/ife/ife.c:168)
[  138.425859][    C1]  kasan_report (mm/kasan/report.c:221 mm/kasan/report.c:597)
[  138.425868][    C1]  ? ife_tlv_meta_encode (net/ife/ife.c:168)
[  138.425878][    C1]  kasan_check_range (mm/kasan/generic.c:186 (discriminator 1) mm/kasan/generic.c:200 (discriminator 1))
[  138.425884][    C1]  __asan_memset (mm/kasan/shadow.c:84 (discriminator 2))
[  138.425889][    C1]  ife_tlv_meta_encode (net/ife/ife.c:168)
[  138.425893][    C1]  ? ife_tlv_meta_encode (net/ife/ife.c:171)
[  138.425898][    C1]  ? srso_alias_return_thunk (arch/x86/lib/retpoline.S:221)
[  138.425903][    C1]  ife_encode_meta_u16 (net/sched/act_ife.c:57)
[  138.425910][    C1]  ? __pfx_do_raw_spin_lock (kernel/locking/spinlock_debug.c:114)
[  138.425916][    C1]  ? __asan_memcpy (mm/kasan/shadow.c:105 (discriminator 3))
[  138.425921][    C1]  ? __pfx_ife_encode_meta_u16 (net/sched/act_ife.c:45)
[  138.425927][    C1]  ? srso_alias_return_thunk (arch/x86/lib/retpoline.S:221)
[  138.425931][    C1]  tcf_ife_act (net/sched/act_ife.c:847 net/sched/act_ife.c:879)

To solve this issue, fix the replace behavior by adding the metalist to
the ife rcu data structure.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/56ade7ddea6ce605552341785d08e365c3f61861
- https://git.kernel.org/stable/c/5b1449301ca070814d866990b46f48d3f39ea4ee
- https://git.kernel.org/stable/c/691866c4cca54dc4df762276b49e89b36e046947
- https://git.kernel.org/stable/c/91a89d3bdc2f63d983adc13d1771631663c5dc1b
- https://git.kernel.org/stable/c/cd888c3966672239f2e0707b846a5a936ac9038a
- https://git.kernel.org/stable/c/e2cedd400c3ec0302ffca2490e8751772906ac23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23378.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23378
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
