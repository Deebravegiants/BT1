# [H] nfsd: cancel nfsd_shrinker_work using sync mode in nfs4_state_shutdown_net

## Summary
Severity: High
Advisory: CVE-2024-50121
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50121
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.123, >=6.2.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: cancel nfsd_shrinker_work using sync mode in nfs4_state_shutdown_net

In the normal case, when we excute `echo 0 > /proc/fs/nfsd/threads`, the
function `nfs4_state_destroy_net` in `nfs4_state_shutdown_net` will
release all resources related to the hashed `nfs4_client`. If the
`nfsd_client_shrinker` is running concurrently, the `expire_client`
function will first unhash this client and then destroy it. This can
lead to the following warning. Additionally, numerous use-after-free
errors may occur as well.

nfsd_client_shrinker         echo 0 > /proc/fs/nfsd/threads

expire_client                nfsd_shutdown_net
  unhash_client                ...
                               nfs4_state_shutdown_net
                                 /* won't wait shrinker exit */
  /*                             cancel_work(&nn->nfsd_shrinker_work)
   * nfsd_file for this          /* won't destroy unhashed client1 */
   * client1 still alive         nfs4_state_destroy_net
   */

                               nfsd_file_cache_shutdown
                                 /* trigger warning */
                                 kmem_cache_destroy(nfsd_file_slab)
                                 kmem_cache_destroy(nfsd_file_mark_slab)
  /* release nfsd_file and mark */
  __destroy_client

====================================================================
BUG nfsd_file (Not tainted): Objects remaining in nfsd_file on
__kmem_cache_shutdown()
--------------------------------------------------------------------
CPU: 4 UID: 0 PID: 764 Comm: sh Not tainted 6.12.0-rc3+ #1

 dump_stack_lvl+0x53/0x70
 slab_err+0xb0/0xf0
 __kmem_cache_shutdown+0x15c/0x310
 kmem_cache_destroy+0x66/0x160
 nfsd_file_cache_shutdown+0xac/0x210 [nfsd]
 nfsd_destroy_serv+0x251/0x2a0 [nfsd]
 nfsd_svc+0x125/0x1e0 [nfsd]
 write_threads+0x16a/0x2a0 [nfsd]
 nfsctl_transaction_write+0x74/0xa0 [nfsd]
 vfs_write+0x1a5/0x6d0
 ksys_write+0xc1/0x160
 do_syscall_64+0x5f/0x170
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

====================================================================
BUG nfsd_file_mark (Tainted: G    B   W         ): Objects remaining
nfsd_file_mark on __kmem_cache_shutdown()
--------------------------------------------------------------------

 dump_stack_lvl+0x53/0x70
 slab_err+0xb0/0xf0
 __kmem_cache_shutdown+0x15c/0x310
 kmem_cache_destroy+0x66/0x160
 nfsd_file_cache_shutdown+0xc8/0x210 [nfsd]
 nfsd_destroy_serv+0x251/0x2a0 [nfsd]
 nfsd_svc+0x125/0x1e0 [nfsd]
 write_threads+0x16a/0x2a0 [nfsd]
 nfsctl_transaction_write+0x74/0xa0 [nfsd]
 vfs_write+0x1a5/0x6d0
 ksys_write+0xc1/0x160
 do_syscall_64+0x5f/0x170
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

To resolve this issue, cancel `nfsd_shrinker_work` using synchronous
mode in nfs4_state_shutdown_net.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/36775f42e039b01d4abe8998bf66771a37d3cdcc
- https://git.kernel.org/stable/c/5ade4382de16c34d9259cb548f36ec5c4555913c
- https://git.kernel.org/stable/c/add1df5eba163a3a6ece11cb85890e2e410baaea
- https://git.kernel.org/stable/c/d5ff2fb2e7167e9483846e34148e60c0c016a1f6
- https://git.kernel.org/stable/c/f67138dd338cb564ade7d3755c8cd4f68b46d397
- https://git.kernel.org/stable/c/f965dc0f099a54fca100acf6909abe52d0c85328
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50121.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50121
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
