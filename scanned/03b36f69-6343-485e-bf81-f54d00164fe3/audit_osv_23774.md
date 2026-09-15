# [H] rtw89: cfo: check mac_id to avoid out-of-bounds

## Summary
Severity: High
Advisory: CVE-2022-49471
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49471
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtw89: cfo: check mac_id to avoid out-of-bounds

Somehow, hardware reports incorrect mac_id and pollute memory. Check index
before we access the array.

  UBSAN: array-index-out-of-bounds in rtw89/phy.c:2517:23
  index 188 is out of range for type 's32 [64]'
  CPU: 1 PID: 51550 Comm: irq/35-rtw89_pc Tainted: G           OE
  Call Trace:
   <IRQ>
   show_stack+0x52/0x58
   dump_stack_lvl+0x4c/0x63
   dump_stack+0x10/0x12
   ubsan_epilogue+0x9/0x45
   __ubsan_handle_out_of_bounds.cold+0x44/0x49
   ? __alloc_skb+0x92/0x1d0
   rtw89_phy_cfo_parse+0x44/0x7f [rtw89_core]
   rtw89_core_rx+0x261/0x871 [rtw89_core]
   ? __alloc_skb+0xee/0x1d0
   rtw89_pci_napi_poll+0x3fa/0x4ea [rtw89_pci]
   __napi_poll+0x33/0x1a0
   net_rx_action+0x126/0x260
   ? __queue_work+0x217/0x4c0
   __do_softirq+0xd9/0x315
   ? disable_irq_nosync+0x10/0x10
   do_softirq.part.0+0x6d/0x90
   </IRQ>
   <TASK>
   __local_bh_enable_ip+0x62/0x70
   rtw89_pci_interrupt_threadfn+0x182/0x1a6 [rtw89_pci]
   irq_thread_fn+0x28/0x60
   irq_thread+0xc8/0x190
   ? irq_thread_fn+0x60/0x60
   kthread+0x16b/0x190
   ? irq_thread_check_affinity+0xe0/0xe0
   ? set_kthread_struct+0x50/0x50
   ret_from_fork+0x22/0x30
   </TASK>

## References
- https://git.kernel.org/stable/c/03ed236480aeec8c2fd327a1ea6d711364c495e3
- https://git.kernel.org/stable/c/97df85871a5b187609d30fca6d85b912d9e02f29
- https://git.kernel.org/stable/c/c32fafe68298bb599e825c298e1d0ba30186f0a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49471.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49471
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
