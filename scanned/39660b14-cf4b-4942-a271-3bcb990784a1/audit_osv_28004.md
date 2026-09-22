# [H] nfs: fix UAF in direct writes

## Summary
Severity: High
Advisory: CVE-2024-26958
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26958
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.4.297, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfs: fix UAF in direct writes

In production we have been hitting the following warning consistently

------------[ cut here ]------------
refcount_t: underflow; use-after-free.
WARNING: CPU: 17 PID: 1800359 at lib/refcount.c:28 refcount_warn_saturate+0x9c/0xe0
Workqueue: nfsiod nfs_direct_write_schedule_work [nfs]
RIP: 0010:refcount_warn_saturate+0x9c/0xe0
PKRU: 55555554
Call Trace:
 <TASK>
 ? __warn+0x9f/0x130
 ? refcount_warn_saturate+0x9c/0xe0
 ? report_bug+0xcc/0x150
 ? handle_bug+0x3d/0x70
 ? exc_invalid_op+0x16/0x40
 ? asm_exc_invalid_op+0x16/0x20
 ? refcount_warn_saturate+0x9c/0xe0
 nfs_direct_write_schedule_work+0x237/0x250 [nfs]
 process_one_work+0x12f/0x4a0
 worker_thread+0x14e/0x3b0
 ? ZSTD_getCParams_internal+0x220/0x220
 kthread+0xdc/0x120
 ? __btf_name_valid+0xa0/0xa0
 ret_from_fork+0x1f/0x30

This is because we're completing the nfs_direct_request twice in a row.

The source of this is when we have our commit requests to submit, we
process them and send them off, and then in the completion path for the
commit requests we have

if (nfs_commit_end(cinfo.mds))
	nfs_direct_write_complete(dreq);

However since we're submitting asynchronous requests we sometimes have
one that completes before we submit the next one, so we end up calling
complete on the nfs_direct_request twice.

The only other place we use nfs_generic_commit_list() is in
__nfs_commit_inode, which wraps this call in a

nfs_commit_begin();
nfs_commit_end();

Which is a common pattern for this style of completion handling, one
that is also repeated in the direct code with get_dreq()/put_dreq()
calls around where we process events as well as in the completion paths.

Fix this by using the same pattern for the commit requests.

Before with my 200 node rocksdb stress running this warning would pop
every 10ish minutes.  With my patch the stress test has been running for
several hours without popping.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/17f46b803d4f23c66cacce81db35fef3adb8f2af
- https://git.kernel.org/stable/c/1daf52b5ffb24870fbeda20b4967526d8f9e12ab
- https://git.kernel.org/stable/c/3abc2d160ed8213948b147295d77d44a22c88fa3
- https://git.kernel.org/stable/c/4595d90b5d2ea5fa4d318d13f59055aa4bf3e7f5
- https://git.kernel.org/stable/c/6cd3f13aaa62970b5169d990e936b2e96943bc6a
- https://git.kernel.org/stable/c/80d24b308b7ee7037fc90d8ac99f6f78df0a256f
- https://git.kernel.org/stable/c/cf54f66e1dd78990ec6b32177bca7e6ea2144a95
- https://git.kernel.org/stable/c/e25447c35f8745337ea8bc0c9697fcac14df8605
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26958.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26958
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
