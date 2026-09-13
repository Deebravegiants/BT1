# [H] thunderbolt: Fix KASAN reported stack out-of-bounds read in tb_retimer_scan()

## Summary
Severity: High
Advisory: CVE-2024-50227
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50227
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

thunderbolt: Fix KASAN reported stack out-of-bounds read in tb_retimer_scan()

KASAN reported following issue:

 BUG: KASAN: stack-out-of-bounds in tb_retimer_scan+0xffe/0x1550 [thunderbolt]
 Read of size 4 at addr ffff88810111fc1c by task kworker/u56:0/11
 CPU: 0 UID: 0 PID: 11 Comm: kworker/u56:0 Tainted: G     U             6.11.0+ #1387
 Tainted: [U]=USER
 Workqueue: thunderbolt0 tb_handle_hotplug [thunderbolt]
 Call Trace:
  <TASK>
  dump_stack_lvl+0x6c/0x90
  print_report+0xd1/0x630
  kasan_report+0xdb/0x110
  __asan_report_load4_noabort+0x14/0x20
  tb_retimer_scan+0xffe/0x1550 [thunderbolt]
  tb_scan_port+0xa6f/0x2060 [thunderbolt]
  tb_handle_hotplug+0x17b1/0x3080 [thunderbolt]
  process_one_work+0x626/0x1100
  worker_thread+0x6c8/0xfa0
  kthread+0x2c8/0x3a0
  ret_from_fork+0x3a/0x80
  ret_from_fork_asm+0x1a/0x30

This happens because the loop variable still gets incremented by one so
max becomes 3 instead of 2, and this makes the second loop read past the
the array declared on the stack.

Fix this by assigning to max directly in the loop body.

## References
- https://git.kernel.org/stable/c/08b2771e9270fbe1ed4fbbe93abe05ac7fe9861d
- https://git.kernel.org/stable/c/e9e1b20fae7de06ba36dd3f8dba858157bad233d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50227.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50227
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
