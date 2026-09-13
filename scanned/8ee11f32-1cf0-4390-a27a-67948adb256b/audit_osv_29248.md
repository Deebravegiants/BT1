# [H] cachefiles: wait for ondemand_object_worker to finish when dropping object

## Summary
Severity: High
Advisory: CVE-2024-41051
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41051
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

cachefiles: wait for ondemand_object_worker to finish when dropping object

When queuing ondemand_object_worker() to re-open the object,
cachefiles_object is not pinned. The cachefiles_object may be freed when
the pending read request is completed intentionally and the related
erofs is umounted. If ondemand_object_worker() runs after the object is
freed, it will incur use-after-free problem as shown below.

process A  processs B  process C  process D

cachefiles_ondemand_send_req()
// send a read req X
// wait for its completion

           // close ondemand fd
           cachefiles_ondemand_fd_release()
           // set object as CLOSE

                       cachefiles_ondemand_daemon_read()
                       // set object as REOPENING
                       queue_work(fscache_wq, &info->ondemand_work)

                                // close /dev/cachefiles
                                cachefiles_daemon_release
                                cachefiles_flush_reqs
                                complete(&req->done)

// read req X is completed
// umount the erofs fs
cachefiles_put_object()
// object will be freed
cachefiles_ondemand_deinit_obj_info()
kmem_cache_free(object)
                       // both info and object are freed
                       ondemand_object_worker()

When dropping an object, it is no longer necessary to reopen the object,
so use cancel_work_sync() to cancel or wait for ondemand_object_worker()
to finish.

## References
- https://git.kernel.org/stable/c/12e009d60852f7bce0afc373ca0b320f14150418
- https://git.kernel.org/stable/c/b26525b2183632f16a3a4108fe6a4bfa8afac6ed
- https://git.kernel.org/stable/c/d3179bae72b1b5e555ba839d6d9f40a350a4d78a
- https://git.kernel.org/stable/c/ec9289369259d982e735a71437e32e6b4035290c
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41051.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41051
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
