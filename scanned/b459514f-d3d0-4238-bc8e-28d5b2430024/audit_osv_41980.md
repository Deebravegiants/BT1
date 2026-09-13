# [H] KVM: x86: hyper-v: Bound the bank index when querying sparse banks

## Summary
Severity: High
Advisory: CVE-2026-64247
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64247
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: hyper-v: Bound the bank index when querying sparse banks

When checking if a VP ID is included in a sparse bank set, explicitly check
that the ID can actually be contained in a sparse bank (the TLFS allows for
a maximum of 64 banks of 64 vCPUs each).  When handling a paravirtual TLB
flush for L2, the VP ID is copied verbatim from the enlightened VMCS,
without any bounds check, i.e. isn't guaranteed to be under the limit of
4096.

Failure to check the bounds of the VP ID leads to an out-of-bounds read
when testing the sparse bank, and super strictly speaking could lead to KVM
performing an unnecessary TLB flush for an L2 vCPU.

  ==================================================================
  BUG: KASAN: use-after-free in hv_is_vp_in_sparse_set+0x85/0x100 [kvm]
  Read of size 8 at addr ffff88811ba5f598 by task hyperv_evmcs/2802

  CPU: 12 UID: 1000 PID: 2802 Comm: hyperv_evmcs Not tainted 7.1.0-rc2 #7 PREEMPT
  Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 0.0.0 02/06/2015
  Call Trace:
   <TASK>
   dump_stack_lvl+0x51/0x60
   print_report+0xcb/0x5d0
   kasan_report+0xb4/0xe0
   kasan_check_range+0x35/0x1b0
   hv_is_vp_in_sparse_set+0x85/0x100 [kvm]
   kvm_hv_flush_tlb+0xe9e/0x16c0 [kvm]
   kvm_hv_hypercall+0xe6b/0x1e60 [kvm]
   vmx_handle_exit+0x485/0x1b60 [kvm_intel]
   kvm_arch_vcpu_ioctl_run+0x22e3/0x5070 [kvm]
   kvm_vcpu_ioctl+0x5d0/0x10c0 [kvm]
   __x64_sys_ioctl+0x129/0x1a0
   do_syscall_64+0xb9/0xcf0
   entry_SYSCALL_64_after_hwframe+0x4b/0x53
  RIP: 0033:0x7f0e62d1a9bf
   </TASK>

  The buggy address belongs to the physical page:
  page: refcount:0 mapcount:0 mapping:0000000000000000 index:0xffffffffffffffff pfn:0x11ba5f
  flags: 0x4000000000000000(zone=1)
  raw: 4000000000000000 0000000000000000 00000000ffffffff 0000000000000000
  raw: ffffffffffffffff 0000000000000000 00000000ffffffff 0000000000000000
  page dumped because: kasan: bad access detected

  Memory state around the buggy address:
   ffff88811ba5f480: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
   ffff88811ba5f500: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  >ffff88811ba5f580: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
                              ^
   ffff88811ba5f600: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
   ffff88811ba5f680: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  ==================================================================
  Disabling lock debugging due to kernel taint

Opportunistically add a compile time assertion to ensure the maximum number
of sparse banks exactly matches the number of possible bits in the passed
in mask.

[sean: add KASAN splat, drop comment, add assert, massage changelog]

## References
- https://git.kernel.org/stable/c/4721f8160f17554b003e8928bb61e6c9b2fe92a3
- https://git.kernel.org/stable/c/83c2f52c6a78b1590034e955cff3fe0b052fe4ae
- https://git.kernel.org/stable/c/d18756b12aab30d07794446445c93112e5c69a2e
- https://git.kernel.org/stable/c/e36095d8d922bb26ce860231aacf0cd14edea07c
- https://git.kernel.org/stable/c/f636cf6a1e7b7f40d48d8d08bd5f152aa61dd130
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64247.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64247
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
