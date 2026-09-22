# [H] net: ena: fix shift-out-of-bounds in exponential backoff

## Summary
Severity: High
Advisory: CVE-2023-53272
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53272
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ena: fix shift-out-of-bounds in exponential backoff

The ENA adapters on our instances occasionally reset.  Once recently
logged a UBSAN failure to console in the process:

  UBSAN: shift-out-of-bounds in build/linux/drivers/net/ethernet/amazon/ena/ena_com.c:540:13
  shift exponent 32 is too large for 32-bit type 'unsigned int'
  CPU: 28 PID: 70012 Comm: kworker/u72:2 Kdump: loaded not tainted 5.15.117
  Hardware name: Amazon EC2 c5d.9xlarge/, BIOS 1.0 10/16/2017
  Workqueue: ena ena_fw_reset_device [ena]
  Call Trace:
  <TASK>
  dump_stack_lvl+0x4a/0x63
  dump_stack+0x10/0x16
  ubsan_epilogue+0x9/0x36
  __ubsan_handle_shift_out_of_bounds.cold+0x61/0x10e
  ? __const_udelay+0x43/0x50
  ena_delay_exponential_backoff_us.cold+0x16/0x1e [ena]
  wait_for_reset_state+0x54/0xa0 [ena]
  ena_com_dev_reset+0xc8/0x110 [ena]
  ena_down+0x3fe/0x480 [ena]
  ena_destroy_device+0xeb/0xf0 [ena]
  ena_fw_reset_device+0x30/0x50 [ena]
  process_one_work+0x22b/0x3d0
  worker_thread+0x4d/0x3f0
  ? process_one_work+0x3d0/0x3d0
  kthread+0x12a/0x150
  ? set_kthread_struct+0x50/0x50
  ret_from_fork+0x22/0x30
  </TASK>

Apparently, the reset delays are getting so large they can trigger a
UBSAN panic.

Looking at the code, the current timeout is capped at 5000us.  Using a
base value of 100us, the current code will overflow after (1<<29).  Even
at values before 32, this function wraps around, perhaps
unintentionally.

Cap the value of the exponent used for this backoff at (1<<16) which is
larger than currently necessary, but large enough to support bigger
values in the future.

## References
- https://git.kernel.org/stable/c/0939c264729d4a081ff88efce2ffdf85dc5331e0
- https://git.kernel.org/stable/c/1e760b2d18bf129b3da052c2946c02758e97d15e
- https://git.kernel.org/stable/c/1e9cb763e9bacf0c932aa948f50dcfca6f519a26
- https://git.kernel.org/stable/c/3e36cc94d6e60a27f27498adf1c71eeba769ab33
- https://git.kernel.org/stable/c/90947ebf8794e3c229fb2e16e37f1bfea6877f14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53272.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53272
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
