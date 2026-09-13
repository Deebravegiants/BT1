# [H] net/smc: Transitional solution for clcsock race issue

## Summary
Severity: High
Advisory: CVE-2022-48751
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48751
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.15.19, >=5.16.0 <5.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: Transitional solution for clcsock race issue

We encountered a crash in smc_setsockopt() and it is caused by
accessing smc->clcsock after clcsock was released.

 BUG: kernel NULL pointer dereference, address: 0000000000000020
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 PGD 0 P4D 0
 Oops: 0000 [#1] PREEMPT SMP PTI
 CPU: 1 PID: 50309 Comm: nginx Kdump: loaded Tainted: G E     5.16.0-rc4+ #53
 RIP: 0010:smc_setsockopt+0x59/0x280 [smc]
 Call Trace:
  <TASK>
  __sys_setsockopt+0xfc/0x190
  __x64_sys_setsockopt+0x20/0x30
  do_syscall_64+0x34/0x90
  entry_SYSCALL_64_after_hwframe+0x44/0xae
 RIP: 0033:0x7f16ba83918e
  </TASK>

This patch tries to fix it by holding clcsock_release_lock and
checking whether clcsock has already been released before access.

In case that a crash of the same reason happens in smc_getsockopt()
or smc_switch_to_fallback(), this patch also checkes smc->clcsock
in them too. And the caller of smc_switch_to_fallback() will identify
whether fallback succeeds according to the return value.

## References
- https://git.kernel.org/stable/c/38f0bdd548fd2ef5d481b88d8a2bfef968452e34
- https://git.kernel.org/stable/c/4284225cd8001e134f5cf533a7cd244bbb654d0f
- https://git.kernel.org/stable/c/c0bf3d8a943b6f2e912b7c1de03e2ef28e76f760
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48751.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48751
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
