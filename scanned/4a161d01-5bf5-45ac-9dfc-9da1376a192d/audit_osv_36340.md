# [H] nvmet: fix race in nvmet_bio_done() leading to NULL pointer dereference

## Summary
Severity: High
Advisory: CVE-2026-23148
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23148
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.69, >=6.13.0 <6.18.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: fix race in nvmet_bio_done() leading to NULL pointer dereference

There is a race condition in nvmet_bio_done() that can cause a NULL
pointer dereference in blk_cgroup_bio_start():

1. nvmet_bio_done() is called when a bio completes
2. nvmet_req_complete() is called, which invokes req->ops->queue_response(req)
3. The queue_response callback can re-queue and re-submit the same request
4. The re-submission reuses the same inline_bio from nvmet_req
5. Meanwhile, nvmet_req_bio_put() (called after nvmet_req_complete)
   invokes bio_uninit() for inline_bio, which sets bio->bi_blkg to NULL
6. The re-submitted bio enters submit_bio_noacct_nocheck()
7. blk_cgroup_bio_start() dereferences bio->bi_blkg, causing a crash:

  BUG: kernel NULL pointer dereference, address: 0000000000000028
  #PF: supervisor read access in kernel mode
  RIP: 0010:blk_cgroup_bio_start+0x10/0xd0
  Call Trace:
   submit_bio_noacct_nocheck+0x44/0x250
   nvmet_bdev_execute_rw+0x254/0x370 [nvmet]
   process_one_work+0x193/0x3c0
   worker_thread+0x281/0x3a0

Fix this by reordering nvmet_bio_done() to call nvmet_req_bio_put()
BEFORE nvmet_req_complete(). This ensures the bio is cleaned up before
the request can be re-submitted, preventing the race condition.

## References
- https://git.kernel.org/stable/c/0fcee2cfc4b2e16e62ff8e0cc2cd8dd24efad65e
- https://git.kernel.org/stable/c/68207ceefd71cc74ce4e983fa9bd10c3122e349b
- https://git.kernel.org/stable/c/ee10b06980acca1d46e0fa36d6fb4a9578eab6e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23148.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23148
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
