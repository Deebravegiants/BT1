# [H] net/smc: initialize close_work early to avoid warning

## Summary
Severity: High
Advisory: CVE-2024-56641
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56641
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: initialize close_work early to avoid warning

We encountered a warning that close_work was canceled before
initialization.

  WARNING: CPU: 7 PID: 111103 at kernel/workqueue.c:3047 __flush_work+0x19e/0x1b0
  Workqueue: events smc_lgr_terminate_work [smc]
  RIP: 0010:__flush_work+0x19e/0x1b0
  Call Trace:
   ? __wake_up_common+0x7a/0x190
   ? work_busy+0x80/0x80
   __cancel_work_timer+0xe3/0x160
   smc_close_cancel_work+0x1a/0x70 [smc]
   smc_close_active_abort+0x207/0x360 [smc]
   __smc_lgr_terminate.part.38+0xc8/0x180 [smc]
   process_one_work+0x19e/0x340
   worker_thread+0x30/0x370
   ? process_one_work+0x340/0x340
   kthread+0x117/0x130
   ? __kthread_cancel_work+0x50/0x50
   ret_from_fork+0x22/0x30

This is because when smc_close_cancel_work is triggered, e.g. the RDMA
driver is rmmod and the LGR is terminated, the conn->close_work is
flushed before initialization, resulting in WARN_ON(!work->func).

__smc_lgr_terminate             | smc_connect_{rdma|ism}
-------------------------------------------------------------
                                | smc_conn_create
				| \- smc_lgr_register_conn
for conn in lgr->conns_all      |
\- smc_conn_kill                |
   \- smc_close_active_abort    |
      \- smc_close_cancel_work  |
         \- cancel_work_sync    |
            \- __flush_work     |
	         (close_work)   |
	                        | smc_close_init
	                        | \- INIT_WORK(&close_work)

So fix this by initializing close_work before establishing the
connection.

## References
- https://git.kernel.org/stable/c/0541db8ee32c09463a72d0987382b3a3336b0043
- https://git.kernel.org/stable/c/6638e52dcfafaf1b9cbc34544f0c832db0069ea1
- https://git.kernel.org/stable/c/f0c37002210aaede10dae849d1a78efc2243add2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56641.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56641
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
