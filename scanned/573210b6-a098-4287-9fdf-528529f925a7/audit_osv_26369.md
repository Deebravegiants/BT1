# [M] riscv: kprobe: Fixup kernel panic when probing an illegal position

## Summary
Severity: Medium
Advisory: CVE-2023-52978
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52978
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: kprobe: Fixup kernel panic when probing an illegal position

The kernel would panic when probed for an illegal position. eg:

(CONFIG_RISCV_ISA_C=n)

echo 'p:hello kernel_clone+0x16 a0=%a0' >> kprobe_events
echo 1 > events/kprobes/hello/enable
cat trace

Kernel panic - not syncing: stack-protector: Kernel stack
is corrupted in: __do_sys_newfstatat+0xb8/0xb8
CPU: 0 PID: 111 Comm: sh Not tainted
6.2.0-rc1-00027-g2d398fe49a4d #490
Hardware name: riscv-virtio,qemu (DT)
Call Trace:
[<ffffffff80007268>] dump_backtrace+0x38/0x48
[<ffffffff80c5e83c>] show_stack+0x50/0x68
[<ffffffff80c6da28>] dump_stack_lvl+0x60/0x84
[<ffffffff80c6da6c>] dump_stack+0x20/0x30
[<ffffffff80c5ecf4>] panic+0x160/0x374
[<ffffffff80c6db94>] generic_handle_arch_irq+0x0/0xa8
[<ffffffff802deeb0>] sys_newstat+0x0/0x30
[<ffffffff800158c0>] sys_clone+0x20/0x30
[<ffffffff800039e8>] ret_from_syscall+0x0/0x4
---[ end Kernel panic - not syncing: stack-protector:
Kernel stack is corrupted in: __do_sys_newfstatat+0xb8/0xb8 ]---

That is because the kprobe's ebreak instruction broke the kernel's
original code. The user should guarantee the correction of the probe
position, but it couldn't make the kernel panic.

This patch adds arch_check_kprobe in arch_prepare_kprobe to prevent an
illegal position (Such as the middle of an instruction).

## References
- https://git.kernel.org/stable/c/04a73558209554da17f46490ec4faaaf1b2bab68
- https://git.kernel.org/stable/c/12316538b1d193064109ce1a28fc9bacd43950de
- https://git.kernel.org/stable/c/87f48c7ccc73afc78630530d9af51f458f58cab8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52978.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52978
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
