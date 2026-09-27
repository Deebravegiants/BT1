# [H] KVM: x86: Use scratch field in MMIO fragment to hold small write values

## Summary
Severity: High
Advisory: CVE-2026-31588
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31588
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Use scratch field in MMIO fragment to hold small write values

When exiting to userspace to service an emulated MMIO write, copy the
to-be-written value to a scratch field in the MMIO fragment if the size
of the data payload is 8 bytes or less, i.e. can fit in a single chunk,
instead of pointing the fragment directly at the source value.

This fixes a class of use-after-free bugs that occur when the emulator
initiates a write using an on-stack, local variable as the source, the
write splits a page boundary, *and* both pages are MMIO pages.  Because
KVM's ABI only allows for physically contiguous MMIO requests, accesses
that split MMIO pages are separated into two fragments, and are sent to
userspace one at a time.  When KVM attempts to complete userspace MMIO in
response to KVM_RUN after the first fragment, KVM will detect the second
fragment and generate a second userspace exit, and reference the on-stack
variable.

The issue is most visible if the second KVM_RUN is performed by a separate
task, in which case the stack of the initiating task can show up as truly
freed data.

  ==================================================================
  BUG: KASAN: use-after-free in complete_emulated_mmio+0x305/0x420
  Read of size 1 at addr ffff888009c378d1 by task syz-executor417/984

  CPU: 1 PID: 984 Comm: syz-executor417 Not tainted 5.10.0-182.0.0.95.h2627.eulerosv2r13.x86_64 #3
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.15.0-0-g2dd4b9b3f840-prebuilt.qemu.org 04/01/2014 Call Trace:
  dump_stack+0xbe/0xfd
  print_address_description.constprop.0+0x19/0x170
  __kasan_report.cold+0x6c/0x84
  kasan_report+0x3a/0x50
  check_memory_region+0xfd/0x1f0
  memcpy+0x20/0x60
  complete_emulated_mmio+0x305/0x420
  kvm_arch_vcpu_ioctl_run+0x63f/0x6d0
  kvm_vcpu_ioctl+0x413/0xb20
  __se_sys_ioctl+0x111/0x160
  do_syscall_64+0x30/0x40
  entry_SYSCALL_64_after_hwframe+0x67/0xd1
  RIP: 0033:0x42477d
  Code: <48> 3d 01 f0 ff ff 73 01 c3 48 c7 c1 b0 ff ff ff f7 d8 64 89 01 48
  RSP: 002b:00007faa8e6890e8 EFLAGS: 00000246 ORIG_RAX: 0000000000000010
  RAX: ffffffffffffffda RBX: 00000000004d7338 RCX: 000000000042477d
  RDX: 0000000000000000 RSI: 000000000000ae80 RDI: 0000000000000005
  RBP: 00000000004d7330 R08: 00007fff28d546df R09: 0000000000000000
  R10: 0000000000000000 R11: 0000000000000246 R12: 00000000004d733c
  R13: 0000000000000000 R14: 000000000040a200 R15: 00007fff28d54720

  The buggy address belongs to the page:
  page:0000000029f6a428 refcount:0 mapcount:0 mapping:0000000000000000 index:0x0 pfn:0x9c37
  flags: 0xfffffc0000000(node=0|zone=1|lastcpupid=0x1fffff)
  raw: 000fffffc0000000 0000000000000000 ffffea0000270dc8 0000000000000000
  raw: 0000000000000000 0000000000000000 00000000ffffffff 0000000000000000 page dumped because: kasan: bad access detected

  Memory state around the buggy address:
  ffff888009c37780: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  ffff888009c37800: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  >ffff888009c37880: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
                                                   ^
  ffff888009c37900: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  ffff888009c37980: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
  ==================================================================

The bug can also be reproduced with a targeted KVM-Unit-Test by hacking
KVM to fill a large on-stack variable in complete_emulated_mmio(), i.e. by
overwrite the data value with garbage.

Limit the use of the scratch fields to 8-byte or smaller accesses, and to
just writes, as larger accesses and reads are not affected thanks to
implementation details in the emulator, but add a sanity check to ensure
those details don't change in the future.  Specifically, KVM never uses
on-stack variables for accesses larger that 8 bytes, e.g. uses an operand
in the emulator context, and *al
---truncated---

## References
- https://git.kernel.org/stable/c/019d0bd32b9a4646ba35d904907452039e2db700
- https://git.kernel.org/stable/c/0b16e69d17d8c35c5c9d5918bf596c75a44655d3
- https://git.kernel.org/stable/c/22d2ff69d487a32a8b88f9c970120fc2daa08a77
- https://git.kernel.org/stable/c/2b83d91e9ae92fe1258d7040a32430bbb3bb7d6e
- https://git.kernel.org/stable/c/3a7b6d75c8f85b09dea893f64a85a356bcf6c3fe
- https://git.kernel.org/stable/c/4569c66dd9e94a22cd0796b6514a8b25ffff16a1
- https://git.kernel.org/stable/c/52570e73d48f1c73836d37e594667117b4c2a5a8
- https://git.kernel.org/stable/c/b5a02d37eb0739f462fa12df449ab9b3480c783b
- https://git.kernel.org/stable/c/dc6a6c3db3a4eca7e747cfc46e22c08d016c68f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31588.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31588
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
