# [H] Bluetooth: bnep: reject short frames before parsing

## Summary
Severity: High
Advisory: CVE-2026-53253
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53253
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: bnep: reject short frames before parsing

A BNEP peer can send a short BNEP SDU. bnep_rx_frame() reads the
packet type byte immediately and, for control packets, reads the control
opcode and setup UUID-size byte before proving that those bytes are
present. bnep_rx_control() also dereferences the control opcode without
rejecting an empty control payload.

Use skb_pull_data() for the fixed fields in bnep_rx_frame() so a NULL
return gates each dereference. Split the control handler so the frame
path can pass an opcode that has already been pulled, and keep the
byte-buffer wrapper for extension control payloads.

For BNEP_SETUP_CONN_REQ, name the UUID-size byte before pulling the
setup payload. struct bnep_setup_conn_req carries destination and source
service UUIDs after that byte, each uuid_size bytes, so the parser now
documents that tuple explicitly instead of leaving the pull length as an
opaque multiplication.

Validation reproduced this kernel report:
KASAN slab-out-of-bounds in bnep_rx_frame.isra.0+0x130c/0x1790
The buggy address belongs to the object at ffff88800c0f7908 which belongs
to the cache kmalloc-8 of size 8
The buggy address is located 0 bytes to the right of allocated 1-byte
region [ffff88800c0f7908, ffff88800c0f7909)
Read of size 1
Call trace:
  dump_stack_lvl+0xb3/0x140 (?:?)
  print_address_description+0x57/0x3a0 (?:?)
  bnep_rx_frame+0x130c/0x1790 (net/bluetooth/bnep/core.c:306)
  print_report+0xb9/0x2b0 (?:?)
  __virt_addr_valid+0x1ba/0x3a0 (?:?)
  srso_alias_return_thunk+0x5/0xfbef5 (?:?)
  kasan_addr_to_slab+0x21/0x60 (?:?)
  kasan_report+0xe0/0x110 (?:?)
  process_one_work+0xfce/0x17e0 (kernel/workqueue.c:3200)
  worker_thread+0x65c/0xe40 (?:?)
  __kthread_parkme+0x184/0x230 (?:?)
  kthread+0x35e/0x470 (?:?)
  _raw_spin_unlock_irq+0x28/0x50 (?:?)
  ret_from_fork+0x586/0x870 (?:?)
  __switch_to+0x74f/0xdc0 (?:?)
  ret_from_fork_asm+0x1a/0x30 (?:?)

## References
- https://git.kernel.org/stable/c/0ef2ea86c82b2615902d085cd5a586fe9f58994f
- https://git.kernel.org/stable/c/2b83afb19293e4de700edae306115f18966dc4f9
- https://git.kernel.org/stable/c/6770d3a8acdf9151769180cc3710346c4cfbe6f0
- https://git.kernel.org/stable/c/691f14b6a48b637655755134f1e551c7c6fedc2e
- https://git.kernel.org/stable/c/be837cd09897e9e6e1958174501d467bdcbcc2bc
- https://git.kernel.org/stable/c/c893e17d2809ec9c4b3f1cdd5847cecbc27a311b
- https://git.kernel.org/stable/c/d76dec1a37122bc16d83d059c08c0512ea8de909
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53253.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
