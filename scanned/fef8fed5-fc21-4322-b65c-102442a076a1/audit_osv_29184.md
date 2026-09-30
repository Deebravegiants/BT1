# [H] cachefiles: remove requests from xarray during flushing requests

## Summary
Severity: High
Advisory: CVE-2024-40900
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40900
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

cachefiles: remove requests from xarray during flushing requests

Even with CACHEFILES_DEAD set, we can still read the requests, so in the
following concurrency the request may be used after it has been freed:

     mount  |   daemon_thread1    |    daemon_thread2
------------------------------------------------------------
 cachefiles_ondemand_init_object
  cachefiles_ondemand_send_req
   REQ_A = kzalloc(sizeof(*req) + data_len)
   wait_for_completion(&REQ_A->done)
            cachefiles_daemon_read
             cachefiles_ondemand_daemon_read
                                  // close dev fd
                                  cachefiles_flush_reqs
                                   complete(&REQ_A->done)
   kfree(REQ_A)
              xa_lock(&cache->reqs);
              cachefiles_ondemand_select_req
                req->msg.opcode != CACHEFILES_OP_READ
                // req use-after-free !!!
              xa_unlock(&cache->reqs);
                                   xa_destroy(&cache->reqs)

Hence remove requests from cache->reqs when flushing them to avoid
accessing freed requests.

## References
- https://git.kernel.org/stable/c/0fc75c5940fa634d84e64c93bfc388e1274ed013
- https://git.kernel.org/stable/c/37e19cf86a520d65de1de9cb330415c332a40d19
- https://git.kernel.org/stable/c/50d0e55356ba5b84ffb51c42704126124257e598
- https://git.kernel.org/stable/c/9f13aacdd4ee9a7644b2a3c96d67113cd083c9c7
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40900.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40900
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
