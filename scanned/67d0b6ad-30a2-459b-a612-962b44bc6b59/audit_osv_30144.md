# [M] LoongArch: Enable IRQ if do_ale() triggered in irq-enabled context

## Summary
Severity: Medium
Advisory: CVE-2024-50111
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50111
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: Enable IRQ if do_ale() triggered in irq-enabled context

Unaligned access exception can be triggered in irq-enabled context such
as user mode, in this case do_ale() may call get_user() which may cause
sleep. Then we will get:

 BUG: sleeping function called from invalid context at arch/loongarch/kernel/access-helper.h:7
 in_atomic(): 0, irqs_disabled(): 1, non_block: 0, pid: 129, name: modprobe
 preempt_count: 0, expected: 0
 RCU nest depth: 0, expected: 0
 CPU: 0 UID: 0 PID: 129 Comm: modprobe Tainted: G        W          6.12.0-rc1+ #1723
 Tainted: [W]=WARN
 Stack : 9000000105e0bd48 0000000000000000 9000000003803944 9000000105e08000
         9000000105e0bc70 9000000105e0bc78 0000000000000000 0000000000000000
         9000000105e0bc78 0000000000000001 9000000185e0ba07 9000000105e0b890
         ffffffffffffffff 9000000105e0bc78 73924b81763be05b 9000000100194500
         000000000000020c 000000000000000a 0000000000000000 0000000000000003
         00000000000023f0 00000000000e1401 00000000072f8000 0000007ffbb0e260
         0000000000000000 0000000000000000 9000000005437650 90000000055d5000
         0000000000000000 0000000000000003 0000007ffbb0e1f0 0000000000000000
         0000005567b00490 0000000000000000 9000000003803964 0000007ffbb0dfec
         00000000000000b0 0000000000000007 0000000000000003 0000000000071c1d
         ...
 Call Trace:
 [<9000000003803964>] show_stack+0x64/0x1a0
 [<9000000004c57464>] dump_stack_lvl+0x74/0xb0
 [<9000000003861ab4>] __might_resched+0x154/0x1a0
 [<900000000380c96c>] emulate_load_store_insn+0x6c/0xf60
 [<9000000004c58118>] do_ale+0x78/0x180
 [<9000000003801bc8>] handle_ale+0x128/0x1e0

So enable IRQ if unaligned access exception is triggered in irq-enabled
context to fix it.

## References
- https://git.kernel.org/stable/c/69cc6fad5df4ce652d969be69acc60e269e5eea1
- https://git.kernel.org/stable/c/8915ed160dbd32b5ef5864df9a9fc11db83a77bb
- https://git.kernel.org/stable/c/afbfb3568d78082078acc8bb2b29bb47af87253c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50111.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50111
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
