# [H] loop: Fix use-after-free issues

## Summary
Severity: High
Advisory: CVE-2023-53111
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53111
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.15.104, >=5.16.0 <6.1.21, >=6.2.0 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

loop: Fix use-after-free issues

do_req_filebacked() calls blk_mq_complete_request() synchronously or
asynchronously when using asynchronous I/O unless memory allocation fails.
Hence, modify loop_handle_cmd() such that it does not dereference 'cmd' nor
'rq' after do_req_filebacked() finished unless we are sure that the request
has not yet been completed. This patch fixes the following kernel crash:

Unable to handle kernel NULL pointer dereference at virtual address 0000000000000054
Call trace:
 css_put.42938+0x1c/0x1ac
 loop_process_work+0xc8c/0xfd4
 loop_rootcg_workfn+0x24/0x34
 process_one_work+0x244/0x558
 worker_thread+0x400/0x8fc
 kthread+0x16c/0x1e0
 ret_from_fork+0x10/0x20

## References
- https://git.kernel.org/stable/c/407badf73ec9fb0d5744bf2ca1745c1818aa222f
- https://git.kernel.org/stable/c/6917395c4667cfb607ed8bf1826205a59414657c
- https://git.kernel.org/stable/c/9b0cb770f5d7b1ff40bea7ca385438ee94570eec
- https://git.kernel.org/stable/c/e3fda704903f6d1fc351412f1bc6620333959ada
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53111.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53111
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
