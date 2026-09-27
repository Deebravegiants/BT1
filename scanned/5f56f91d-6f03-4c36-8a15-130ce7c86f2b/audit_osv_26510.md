# [M] rcu/rcuscale: Stop kfree_scale_thread thread(s) after unloading rcuscale

## Summary
Severity: Medium
Advisory: CVE-2023-53291
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53291
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rcu/rcuscale: Stop kfree_scale_thread thread(s) after unloading rcuscale

Running the 'kfree_rcu_test' test case [1] results in a splat [2].
The root cause is the kfree_scale_thread thread(s) continue running
after unloading the rcuscale module.  This commit fixes that isue by
invoking kfree_scale_cleanup() from rcu_scale_cleanup() when removing
the rcuscale module.

[1] modprobe rcuscale kfree_rcu_test=1
    // After some time
    rmmod rcuscale
    rmmod torture

[2] BUG: unable to handle page fault for address: ffffffffc0601a87
    #PF: supervisor instruction fetch in kernel mode
    #PF: error_code(0x0010) - not-present page
    PGD 11de4f067 P4D 11de4f067 PUD 11de51067 PMD 112f4d067 PTE 0
    Oops: 0010 [#1] PREEMPT SMP NOPTI
    CPU: 1 PID: 1798 Comm: kfree_scale_thr Not tainted 6.3.0-rc1-rcu+ #1
    Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 0.0.0 02/06/2015
    RIP: 0010:0xffffffffc0601a87
    Code: Unable to access opcode bytes at 0xffffffffc0601a5d.
    RSP: 0018:ffffb25bc2e57e18 EFLAGS: 00010297
    RAX: 0000000000000000 RBX: ffffffffc061f0b6 RCX: 0000000000000000
    RDX: 0000000000000000 RSI: ffffffff962fd0de RDI: ffffffff962fd0de
    RBP: ffffb25bc2e57ea8 R08: 0000000000000000 R09: 0000000000000000
    R10: 0000000000000001 R11: 0000000000000001 R12: 0000000000000000
    R13: 0000000000000000 R14: 000000000000000a R15: 00000000001c1dbe
    FS:  0000000000000000(0000) GS:ffff921fa2200000(0000) knlGS:0000000000000000
    CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
    CR2: ffffffffc0601a5d CR3: 000000011de4c006 CR4: 0000000000370ee0
    DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
    DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
    Call Trace:
     <TASK>
     ? kvfree_call_rcu+0xf0/0x3a0
     ? kthread+0xf3/0x120
     ? kthread_complete_and_exit+0x20/0x20
     ? ret_from_fork+0x1f/0x30
     </TASK>
    Modules linked in: rfkill sunrpc ... [last unloaded: torture]
    CR2: ffffffffc0601a87
    ---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/1dd7547c7610723b2b6afe1a3c4ddb2bde63387c
- https://git.kernel.org/stable/c/23fc8df26dead16687ae6eb47b0561a4a832e2f6
- https://git.kernel.org/stable/c/29b1da4f90fc42c91beb4e400d926194925ad31b
- https://git.kernel.org/stable/c/604d6a5ff718874904b0fe614878a42b42c0d699
- https://git.kernel.org/stable/c/b8a6ba524d41f4da102e65f90498d9a910839621
- https://git.kernel.org/stable/c/f766d45ab294871a3d588ee76c666852f151cad9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53291.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53291
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
