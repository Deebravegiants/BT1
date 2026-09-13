# [M] net/smc: fix deadlock triggered by cancel_delayed_work_syn()

## Summary
Severity: Medium
Advisory: CVE-2023-53233
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53233
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.176, >=5.11.0 <5.15.104, >=5.16.0 <6.1.21, >=6.2.0 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix deadlock triggered by cancel_delayed_work_syn()

The following LOCKDEP was detected:
		Workqueue: events smc_lgr_free_work [smc]
		WARNING: possible circular locking dependency detected
		6.1.0-20221027.rc2.git8.56bc5b569087.300.fc36.s390x+debug #1 Not tainted
		------------------------------------------------------
		kworker/3:0/176251 is trying to acquire lock:
		00000000f1467148 ((wq_completion)smc_tx_wq-00000000#2){+.+.}-{0:0},
			at: __flush_workqueue+0x7a/0x4f0
		but task is already holding lock:
		0000037fffe97dc8 ((work_completion)(&(&lgr->free_work)->work)){+.+.}-{0:0},
			at: process_one_work+0x232/0x730
		which lock already depends on the new lock.
		the existing dependency chain (in reverse order) is:
		-> #4 ((work_completion)(&(&lgr->free_work)->work)){+.+.}-{0:0}:
		       __lock_acquire+0x58e/0xbd8
		       lock_acquire.part.0+0xe2/0x248
		       lock_acquire+0xac/0x1c8
		       __flush_work+0x76/0xf0
		       __cancel_work_timer+0x170/0x220
		       __smc_lgr_terminate.part.0+0x34/0x1c0 [smc]
		       smc_connect_rdma+0x15e/0x418 [smc]
		       __smc_connect+0x234/0x480 [smc]
		       smc_connect+0x1d6/0x230 [smc]
		       __sys_connect+0x90/0xc0
		       __do_sys_socketcall+0x186/0x370
		       __do_syscall+0x1da/0x208
		       system_call+0x82/0xb0
		-> #3 (smc_client_lgr_pending){+.+.}-{3:3}:
		       __lock_acquire+0x58e/0xbd8
		       lock_acquire.part.0+0xe2/0x248
		       lock_acquire+0xac/0x1c8
		       __mutex_lock+0x96/0x8e8
		       mutex_lock_nested+0x32/0x40
		       smc_connect_rdma+0xa4/0x418 [smc]
		       __smc_connect+0x234/0x480 [smc]
		       smc_connect+0x1d6/0x230 [smc]
		       __sys_connect+0x90/0xc0
		       __do_sys_socketcall+0x186/0x370
		       __do_syscall+0x1da/0x208
		       system_call+0x82/0xb0
		-> #2 (sk_lock-AF_SMC){+.+.}-{0:0}:
		       __lock_acquire+0x58e/0xbd8
		       lock_acquire.part.0+0xe2/0x248
		       lock_acquire+0xac/0x1c8
		       lock_sock_nested+0x46/0xa8
		       smc_tx_work+0x34/0x50 [smc]
		       process_one_work+0x30c/0x730
		       worker_thread+0x62/0x420
		       kthread+0x138/0x150
		       __ret_from_fork+0x3c/0x58
		       ret_from_fork+0xa/0x40
		-> #1 ((work_completion)(&(&smc->conn.tx_work)->work)){+.+.}-{0:0}:
		       __lock_acquire+0x58e/0xbd8
		       lock_acquire.part.0+0xe2/0x248
		       lock_acquire+0xac/0x1c8
		       process_one_work+0x2bc/0x730
		       worker_thread+0x62/0x420
		       kthread+0x138/0x150
		       __ret_from_fork+0x3c/0x58
		       ret_from_fork+0xa/0x40
		-> #0 ((wq_completion)smc_tx_wq-00000000#2){+.+.}-{0:0}:
		       check_prev_add+0xd8/0xe88
		       validate_chain+0x70c/0xb20
		       __lock_acquire+0x58e/0xbd8
		       lock_acquire.part.0+0xe2/0x248
		       lock_acquire+0xac/0x1c8
		       __flush_workqueue+0xaa/0x4f0
		       drain_workqueue+0xaa/0x158
		       destroy_workqueue+0x44/0x2d8
		       smc_lgr_free+0x9e/0xf8 [smc]
		       process_one_work+0x30c/0x730
		       worker_thread+0x62/0x420
		       kthread+0x138/0x150
		       __ret_from_fork+0x3c/0x58
		       ret_from_fork+0xa/0x40
		other info that might help us debug this:
		Chain exists of:
		  (wq_completion)smc_tx_wq-00000000#2
	  	  --> smc_client_lgr_pending
		  --> (work_completion)(&(&lgr->free_work)->work)
		 Possible unsafe locking scenario:
		       CPU0                    CPU1
		       ----                    ----
		  lock((work_completion)(&(&lgr->free_work)->work));
		                   lock(smc_client_lgr_pending);
		                   lock((work_completion)
					(&(&lgr->free_work)->work));
		  lock((wq_completion)smc_tx_wq-00000000#2);
		 *** DEADLOCK ***
		2 locks held by kworker/3:0/176251:
		 #0: 0000000080183548
			((wq_completion)events){+.+.}-{0:0},
				at: process_one_work+0x232/0x730
		 #1: 0000037fffe97dc8
			((work_completion)
			 (&(&lgr->free_work)->work)){+.+.}-{0:0},
				at: process_one_work+0x232/0x730
		stack backtr
---truncated---

## References
- https://git.kernel.org/stable/c/13085e1b5cab8ad802904d72e6a6dae85ae0cd20
- https://git.kernel.org/stable/c/3517584cf1b35bd02f4a90267ddf9dcf17bd9c87
- https://git.kernel.org/stable/c/9708efad9ba5095b9bb7916e11a135b3bd66c071
- https://git.kernel.org/stable/c/b615238e5bc01e13dc0610febddc1ca99bab1df6
- https://git.kernel.org/stable/c/c9ca2257150272df1b8d9ebe5059197ffea6e913
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53233.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
