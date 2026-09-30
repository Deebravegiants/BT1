# [H] cifs: Fix UAF in cifs_demultiplex_thread()

## Summary
Severity: High
Advisory: CVE-2023-52572
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52572
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <5.4.297, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix UAF in cifs_demultiplex_thread()

There is a UAF when xfstests on cifs:

  BUG: KASAN: use-after-free in smb2_is_network_name_deleted+0x27/0x160
  Read of size 4 at addr ffff88810103fc08 by task cifsd/923

  CPU: 1 PID: 923 Comm: cifsd Not tainted 6.1.0-rc4+ #45
  ...
  Call Trace:
   <TASK>
   dump_stack_lvl+0x34/0x44
   print_report+0x171/0x472
   kasan_report+0xad/0x130
   kasan_check_range+0x145/0x1a0
   smb2_is_network_name_deleted+0x27/0x160
   cifs_demultiplex_thread.cold+0x172/0x5a4
   kthread+0x165/0x1a0
   ret_from_fork+0x1f/0x30
   </TASK>

  Allocated by task 923:
   kasan_save_stack+0x1e/0x40
   kasan_set_track+0x21/0x30
   __kasan_slab_alloc+0x54/0x60
   kmem_cache_alloc+0x147/0x320
   mempool_alloc+0xe1/0x260
   cifs_small_buf_get+0x24/0x60
   allocate_buffers+0xa1/0x1c0
   cifs_demultiplex_thread+0x199/0x10d0
   kthread+0x165/0x1a0
   ret_from_fork+0x1f/0x30

  Freed by task 921:
   kasan_save_stack+0x1e/0x40
   kasan_set_track+0x21/0x30
   kasan_save_free_info+0x2a/0x40
   ____kasan_slab_free+0x143/0x1b0
   kmem_cache_free+0xe3/0x4d0
   cifs_small_buf_release+0x29/0x90
   SMB2_negotiate+0x8b7/0x1c60
   smb2_negotiate+0x51/0x70
   cifs_negotiate_protocol+0xf0/0x160
   cifs_get_smb_ses+0x5fa/0x13c0
   mount_get_conns+0x7a/0x750
   cifs_mount+0x103/0xd00
   cifs_smb3_do_mount+0x1dd/0xcb0
   smb3_get_tree+0x1d5/0x300
   vfs_get_tree+0x41/0xf0
   path_mount+0x9b3/0xdd0
   __x64_sys_mount+0x190/0x1d0
   do_syscall_64+0x35/0x80
   entry_SYSCALL_64_after_hwframe+0x46/0xb0

The UAF is because:

 mount(pid: 921)               | cifsd(pid: 923)
-------------------------------|-------------------------------
                               | cifs_demultiplex_thread
SMB2_negotiate                 |
 cifs_send_recv                |
  compound_send_recv           |
   smb_send_rqst               |
    wait_for_response          |
     wait_event_state      [1] |
                               |  standard_receive3
                               |   cifs_handle_standard
                               |    handle_mid
                               |     mid->resp_buf = buf;  [2]
                               |     dequeue_mid           [3]
     KILL the process      [4] |
    resp_iov[i].iov_base = buf |
 free_rsp_buf              [5] |
                               |   is_network_name_deleted [6]
                               |   callback

1. After send request to server, wait the response until
    mid->mid_state != SUBMITTED;
2. Receive response from server, and set it to mid;
3. Set the mid state to RECEIVED;
4. Kill the process, the mid state already RECEIVED, get 0;
5. Handle and release the negotiate response;
6. UAF.

It can be easily reproduce with add some delay in [3] - [6].

Only sync call has the problem since async call's callback is
executed in cifsd process.

Add an extra state to mark the mid state to READY before wakeup the
waitter, then it can get the resp safely.

## References
- https://git.kernel.org/stable/c/76569e3819e0bb59fc19b1b8688b017e627c268a
- https://git.kernel.org/stable/c/908b3b5e97d25e879de3d1f172a255665491c2c3
- https://git.kernel.org/stable/c/99960d282fba6634fa758df4124cb73ef8a77d8a
- https://git.kernel.org/stable/c/d527f51331cace562393a8038d870b3e9916686f
- https://git.kernel.org/stable/c/ed3b36f351d97dacb62cd0f399e8cf79f73bd30a
- https://git.kernel.org/stable/c/fe87e2d0e6265859c659a3ef1e2559a83c5e8e68
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52572.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52572
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
