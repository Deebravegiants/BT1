# [C] nfsd: fix nfs4_openowner leak when concurrent nfsd4_open occur

## Summary
Severity: Critical
Advisory: CVE-2024-56779
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56779
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix nfs4_openowner leak when concurrent nfsd4_open occur

The action force umount(umount -f) will attempt to kill all rpc_task even
umount operation may ultimately fail if some files remain open.
Consequently, if an action attempts to open a file, it can potentially
send two rpc_task to nfs server.

                   NFS CLIENT
thread1                             thread2
open("file")
...
nfs4_do_open
 _nfs4_do_open
  _nfs4_open_and_get_state
   _nfs4_proc_open
    nfs4_run_open_task
     /* rpc_task1 */
     rpc_run_task
     rpc_wait_for_completion_task

                                    umount -f
                                    nfs_umount_begin
                                     rpc_killall_tasks
                                      rpc_signal_task
     rpc_task1 been wakeup
     and return -512
 _nfs4_do_open // while loop
    ...
    nfs4_run_open_task
     /* rpc_task2 */
     rpc_run_task
     rpc_wait_for_completion_task

While processing an open request, nfsd will first attempt to find or
allocate an nfs4_openowner. If it finds an nfs4_openowner that is not
marked as NFS4_OO_CONFIRMED, this nfs4_openowner will released. Since
two rpc_task can attempt to open the same file simultaneously from the
client to server, and because two instances of nfsd can run
concurrently, this situation can lead to lots of memory leak.
Additionally, when we echo 0 to /proc/fs/nfsd/threads, warning will be
triggered.

                    NFS SERVER
nfsd1                  nfsd2       echo 0 > /proc/fs/nfsd/threads

nfsd4_open
 nfsd4_process_open1
  find_or_alloc_open_stateowner
   // alloc oo1, stateid1
                       nfsd4_open
                        nfsd4_process_open1
                        find_or_alloc_open_stateowner
                        // find oo1, without NFS4_OO_CONFIRMED
                         release_openowner
                          unhash_openowner_locked
                          list_del_init(&oo->oo_perclient)
                          // cannot find this oo
                          // from client, LEAK!!!
                         alloc_stateowner // alloc oo2

 nfsd4_process_open2
  init_open_stateid
  // associate oo1
  // with stateid1, stateid1 LEAK!!!
  nfs4_get_vfs_file
  // alloc nfsd_file1 and nfsd_file_mark1
  // all LEAK!!!

                         nfsd4_process_open2
                         ...

                                    write_threads
                                     ...
                                     nfsd_destroy_serv
                                      nfsd_shutdown_net
                                       nfs4_state_shutdown_net
                                        nfs4_state_destroy_net
                                         destroy_client
                                          __destroy_client
                                          // won't find oo1!!!
                                     nfsd_shutdown_generic
                                      nfsd_file_cache_shutdown
                                       kmem_cache_destroy
                                       for nfsd_file_slab
                                       and nfsd_file_mark_slab
                                       // bark since nfsd_file1
                                       // and nfsd_file_mark1
                                       // still alive

=======================================================================
BUG nfsd_file (Not tainted): Objects remaining in nfsd_file on
__kmem_cache_shutdown()
-----------------------------------------------------------------------

Slab 0xffd4000004438a80 objects=34 used=1 fp=0xff11000110e2ad28
flags=0x17ffffc0000240(workingset|head|node=0|zone=2|lastcpupid=0x1fffff)
CPU: 4 UID: 0 PID: 757 Comm: sh Not tainted 6.12.0-rc6+ #19
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS
1.16.1-2.fc37 04/01/2014
Call Trace:
 <TASK>
 dum
---truncated---

## References
- https://git.kernel.org/stable/c/0ab0a3ad24e970e894abcac58f85c332d1726749
- https://git.kernel.org/stable/c/2d505a801e57428057563762f67a5a62009b2600
- https://git.kernel.org/stable/c/37dfc81266d3a32294524bfadd3396614f8633ee
- https://git.kernel.org/stable/c/45abb68c941ebc9a35c6d3a7b08196712093c636
- https://git.kernel.org/stable/c/6f73f920b7ad0084373e46121d7ac34117aed652
- https://git.kernel.org/stable/c/98100e88dd8865999dc6379a3356cd799795fe7b
- https://git.kernel.org/stable/c/a85364f0d30dee01c5d5b4afa55a9629a8f36d8e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56779.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56779
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
