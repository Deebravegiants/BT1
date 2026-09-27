# [C] nvmet: Fix crash when a namespace is disabled

## Summary
Severity: Critical
Advisory: CVE-2025-21850
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21850
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: Fix crash when a namespace is disabled

The namespace percpu counter protects pending I/O, and we can
only safely diable the namespace once the counter drop to zero.
Otherwise we end up with a crash when running blktests/nvme/058
(eg for loop transport):

[ 2352.930426] [  T53909] Oops: general protection fault, probably for non-canonical address 0xdffffc0000000005: 0000 [#1] PREEMPT SMP KASAN PTI
[ 2352.930431] [  T53909] KASAN: null-ptr-deref in range [0x0000000000000028-0x000000000000002f]
[ 2352.930434] [  T53909] CPU: 3 UID: 0 PID: 53909 Comm: kworker/u16:5 Tainted: G        W          6.13.0-rc6 #232
[ 2352.930438] [  T53909] Tainted: [W]=WARN
[ 2352.930440] [  T53909] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-3.fc41 04/01/2014
[ 2352.930443] [  T53909] Workqueue: nvmet-wq nvme_loop_execute_work [nvme_loop]
[ 2352.930449] [  T53909] RIP: 0010:blkcg_set_ioprio+0x44/0x180

as the queue is already torn down when calling submit_bio();

So we need to init the percpu counter in nvmet_ns_enable(), and
wait for it to drop to zero in nvmet_ns_disable() to avoid having
I/O pending after the namespace has been disabled.

## References
- https://git.kernel.org/stable/c/4082326807072b71496501b6a0c55ffe8d5092a5
- https://git.kernel.org/stable/c/cc0607594f6813342b27c752c6fb6f6eb9980cb5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21850.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21850
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
