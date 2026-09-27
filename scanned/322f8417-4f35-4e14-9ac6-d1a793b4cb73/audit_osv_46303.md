# [H] smb: client: fix use-after-free bug in cifs_debug_data_proc_show()

## Summary
Severity: High
Advisory: CVE-2023-52752
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52752
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix use-after-free bug in cifs_debug_data_proc_show()

Skip SMB sessions that are being teared down
(e.g. @ses->ses_status == SES_EXITING) in cifs_debug_data_proc_show()
to avoid use-after-free in @ses.

This fixes the following GPF when reading from /proc/fs/cifs/DebugData
while mounting and umounting

  [ 816.251274] general protection fault, probably for non-canonical
  address 0x6b6b6b6b6b6b6d81: 0000 [#1] PREEMPT SMP NOPTI
  ...
  [  816.260138] Call Trace:
  [  816.260329]  <TASK>
  [  816.260499]  ? die_addr+0x36/0x90
  [  816.260762]  ? exc_general_protection+0x1b3/0x410
  [  816.261126]  ? asm_exc_general_protection+0x26/0x30
  [  816.261502]  ? cifs_debug_tcon+0xbd/0x240 [cifs]
  [  816.261878]  ? cifs_debug_tcon+0xab/0x240 [cifs]
  [  816.262249]  cifs_debug_data_proc_show+0x516/0xdb0 [cifs]
  [  816.262689]  ? seq_read_iter+0x379/0x470
  [  816.262995]  seq_read_iter+0x118/0x470
  [  816.263291]  proc_reg_read_iter+0x53/0x90
  [  816.263596]  ? srso_alias_return_thunk+0x5/0x7f
  [  816.263945]  vfs_read+0x201/0x350
  [  816.264211]  ksys_read+0x75/0x100
  [  816.264472]  do_syscall_64+0x3f/0x90
  [  816.264750]  entry_SYSCALL_64_after_hwframe+0x6e/0xd8
  [  816.265135] RIP: 0033:0x7fd5e669d381

## References
- https://git.kernel.org/stable/c/0ab6f842452ce2cae04209d4671ac6289d0aef8a
- https://git.kernel.org/stable/c/2abdf136784b7edaec7ffe0f4b461b63f9c4c4de
- https://git.kernel.org/stable/c/336a066990bb3962c46daf574ace596bda9303ce
- https://git.kernel.org/stable/c/558817597d5fbd7af31f891b67b0fd20f0d047b7
- https://git.kernel.org/stable/c/89929ea46f9cc11ba66d2c64713aa5d5dc723b09
- https://git.kernel.org/stable/c/d328c09ee9f15ee5a26431f5aad7c9239fa85e62
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52752.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52752
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
