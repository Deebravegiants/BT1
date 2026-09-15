# [H] thunderbolt: Do not double dequeue a configuration request

## Summary
Severity: High
Advisory: CVE-2025-38174
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38174
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.33, >=6.13.0 <6.14.11, >=6.15.0 <6.15.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

thunderbolt: Do not double dequeue a configuration request

Some of our devices crash in tb_cfg_request_dequeue():

 general protection fault, probably for non-canonical address 0xdead000000000122

 CPU: 6 PID: 91007 Comm: kworker/6:2 Tainted: G U W 6.6.65
 RIP: 0010:tb_cfg_request_dequeue+0x2d/0xa0
 Call Trace:
 <TASK>
 ? tb_cfg_request_dequeue+0x2d/0xa0
 tb_cfg_request_work+0x33/0x80
 worker_thread+0x386/0x8f0
 kthread+0xed/0x110
 ret_from_fork+0x38/0x50
 ret_from_fork_asm+0x1b/0x30

The circumstances are unclear, however, the theory is that
tb_cfg_request_work() can be scheduled twice for a request:
first time via frame.callback from ring_work() and second
time from tb_cfg_request().  Both times kworkers will execute
tb_cfg_request_dequeue(), which results in double list_del()
from the ctl->request_queue (the list poison deference hints
at it: 0xdead000000000122).

Do not dequeue requests that don't have TB_CFG_REQUEST_ACTIVE
bit set.

## References
- https://git.kernel.org/stable/c/0771bcbe2f6e5d5f263cf466efe571d2754a46da
- https://git.kernel.org/stable/c/0a3011d47dbc92a33621861c423cb64833d7fe57
- https://git.kernel.org/stable/c/0f73628e9da1ee39daf5f188190cdbaee5e0c98c
- https://git.kernel.org/stable/c/2f62eda4d974c26bc595425eafd429067541f2c9
- https://git.kernel.org/stable/c/5a057f261539720165d03d85024da2b52e67f63d
- https://git.kernel.org/stable/c/85286e634ebbaf9c0fb1cdf580add2f33fc7628c
- https://git.kernel.org/stable/c/cdb4feab2f39e75a66239e3a112beced279612a8
- https://git.kernel.org/stable/c/e49e994cd83705f7ca30eda1e304abddfd96a37a
- https://git.kernel.org/stable/c/eb2d5e794fb966b3ef8bde99eb8561446a53509f
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38174.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38174
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
