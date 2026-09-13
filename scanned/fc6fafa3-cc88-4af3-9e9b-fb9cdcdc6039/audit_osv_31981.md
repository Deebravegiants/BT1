# [H] ublk: make sure ubq->canceling is set when queue is frozen

## Summary
Severity: High
Advisory: CVE-2025-22068
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22068
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ublk: make sure ubq->canceling is set when queue is frozen

Now ublk driver depends on `ubq->canceling` for deciding if the request
can be dispatched via uring_cmd & io_uring_cmd_complete_in_task().

Once ubq->canceling is set, the uring_cmd can be done via ublk_cancel_cmd()
and io_uring_cmd_done().

So set ubq->canceling when queue is frozen, this way makes sure that the
flag can be observed from ublk_queue_rq() reliably, and avoids
use-after-free on uring_cmd.

## References
- https://git.kernel.org/stable/c/5491400589e7572c2d2627ed6384302f7672aa1d
- https://git.kernel.org/stable/c/7e3497d7dacb5aee69dd9be842b778083cae0e75
- https://git.kernel.org/stable/c/8741d0737921ec1c03cf59aebf4d01400c2b461a
- https://git.kernel.org/stable/c/9158359015f0eda00e521e35b7bc7ebce176aebf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22068.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
