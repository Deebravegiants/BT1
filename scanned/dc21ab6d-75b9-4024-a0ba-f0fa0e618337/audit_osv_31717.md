# [C] smb: client: fix double free of TCP_Server_Info::hostname

## Summary
Severity: Critical
Advisory: CVE-2025-21673
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21673
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix double free of TCP_Server_Info::hostname

When shutting down the server in cifs_put_tcp_session(), cifsd thread
might be reconnecting to multiple DFS targets before it realizes it
should exit the loop, so @server->hostname can't be freed as long as
cifsd thread isn't done.  Otherwise the following can happen:

  RIP: 0010:__slab_free+0x223/0x3c0
  Code: 5e 41 5f c3 cc cc cc cc 4c 89 de 4c 89 cf 44 89 44 24 08 4c 89
  1c 24 e8 fb cf 8e 00 44 8b 44 24 08 4c 8b 1c 24 e9 5f fe ff ff <0f>
  0b 41 f7 45 08 00 0d 21 00 0f 85 2d ff ff ff e9 1f ff ff ff 80
  RSP: 0018:ffffb26180dbfd08 EFLAGS: 00010246
  RAX: ffff8ea34728e510 RBX: ffff8ea34728e500 RCX: 0000000000800068
  RDX: 0000000000800068 RSI: 0000000000000000 RDI: ffff8ea340042400
  RBP: ffffe112041ca380 R08: 0000000000000001 R09: 0000000000000000
  R10: 6170732e31303000 R11: 70726f632e786563 R12: ffff8ea34728e500
  R13: ffff8ea340042400 R14: ffff8ea34728e500 R15: 0000000000800068
  FS: 0000000000000000(0000) GS:ffff8ea66fd80000(0000)
  000000
  CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
  CR2: 00007ffc25376080 CR3: 000000012a2ba001 CR4:
  PKRU: 55555554
  Call Trace:
   <TASK>
   ? show_trace_log_lvl+0x1c4/0x2df
   ? show_trace_log_lvl+0x1c4/0x2df
   ? __reconnect_target_unlocked+0x3e/0x160 [cifs]
   ? __die_body.cold+0x8/0xd
   ? die+0x2b/0x50
   ? do_trap+0xce/0x120
   ? __slab_free+0x223/0x3c0
   ? do_error_trap+0x65/0x80
   ? __slab_free+0x223/0x3c0
   ? exc_invalid_op+0x4e/0x70
   ? __slab_free+0x223/0x3c0
   ? asm_exc_invalid_op+0x16/0x20
   ? __slab_free+0x223/0x3c0
   ? extract_hostname+0x5c/0xa0 [cifs]
   ? extract_hostname+0x5c/0xa0 [cifs]
   ? __kmalloc+0x4b/0x140
   __reconnect_target_unlocked+0x3e/0x160 [cifs]
   reconnect_dfs_server+0x145/0x430 [cifs]
   cifs_handle_standard+0x1ad/0x1d0 [cifs]
   cifs_demultiplex_thread+0x592/0x730 [cifs]
   ? __pfx_cifs_demultiplex_thread+0x10/0x10 [cifs]
   kthread+0xdd/0x100
   ? __pfx_kthread+0x10/0x10
   ret_from_fork+0x29/0x50
   </TASK>

## References
- https://git.kernel.org/stable/c/1ea68070338518a1d31ce71e6abfe1b30001b27a
- https://git.kernel.org/stable/c/a2be5f2ba34d0c6d5ef2624b24e3d852561fcd6a
- https://git.kernel.org/stable/c/fa2f9906a7b333ba757a7dbae0713d8a5396186e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21673.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21673
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
