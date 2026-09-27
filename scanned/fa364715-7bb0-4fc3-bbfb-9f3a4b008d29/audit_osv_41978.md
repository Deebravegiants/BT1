# [H] x86/ftrace: Relocate %rip-relative percpu refs in dynamic trampolines

## Summary
Severity: High
Advisory: CVE-2026-64235
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64235
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/ftrace: Relocate %rip-relative percpu refs in dynamic trampolines

With CONFIG_CALL_DEPTH_TRACKING enabled on an x86 retbleed-affected platform
(eg: Skylake), with retbleed=stuff, registering a dynamic ftrace trampoline
crashes on the first call into the traced function:

  BUG: unable to handle page fault for address: ffff88817ae18880
  #PF: supervisor write access in kernel mode
  #PF: error_code(0x0002) - not-present page
  PGD 4b53067 P4D 4b53067 PUD 0
  Oops: Oops: 0002 [#1] SMP PTI
  CPU: 3 UID: 0 PID: 187 Comm: usleep Not tainted 7.0.10 #243 PREEMPT(full)
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS Arch Linux 1.17.0-2-2 04/01/2014
  Code: 24 78 00 00 00 00 48 89 ea 48 89 54 24 20 48 8b b4 24 b8 00 00 00 48 8b bc 24 b0 00 00 00 48 89 bc 24 80 00 00 00 48 83 ef 05 <65> 48 c1 3d 1f a8 b6 02 05 48 8b 15 f6 00 00 00 4c 89 3c 24 4c 89
  Call Trace:
   <TASK>
   ? find_held_lock
   ? exc_page_fault
   ? lock_release
   ? __x64_sys_clock_nanosleep
   ? lockdep_hardirqs_on_prepare
   ? trace_hardirqs_on
   __x64_sys_clock_nanosleep
   do_syscall_64
   ? exc_page_fault
   ? call_depth_return_thunk
   entry_SYSCALL_64_after_hwframe
  ...
  Kernel panic - not syncing: Fatal exception

This small reproducer allows to easily trigger the crash:

  # echo 'p __x64_sys_clock_nanosleep' > /sys/kernel/tracing/kprobe_events
  # echo 1 > /sys/kernel/tracing/events/kprobes/p___x64_sys_clock_nanosleep_0/enable
  # usleep 1

Monitoring the crash under GDB points to the exact instruction in charge of
incrementing the call depth:

  sarq $5, %gs:__x86_call_depth(%rip)

This instruction matches the one inserted by the ftrace_regs_caller from
ftrace_64.S. This emitted code was likely working fine until the introduction
of

  59bec00ace28 ("x86/percpu: Introduce %rip-relative addressing to PER_CPU_VAR()"):

it has made the call depth accounting addressing relative to $rip, instead of
being based on an absolute address.

As this code exact location depends on where the trampoline lives in memory,
the corresponding displacement needs to be adjusted at runtime to actually
correctly find the per-cpu __x86_call_depth value, otherwise the targeted
address is wrong, leading to the page fault seen above.

Fix the %rip-relative displacement of the copied CALL_DEPTH_ACCOUNT
instruction (from ftrace_regs_caller) by calling text_poke_apply_relocation(),
as it is done for example by the x86 BPF JIT compiler through
x86_call_depth_emit_accounting(). This corrects both CALL_DEPTH_ACCOUNT slots,
in ftrace_caller and ftrace_regs_caller.

  [ bp: Massage. ]

## References
- https://git.kernel.org/stable/c/8093442a2d1d4b42b9340a86023ccb2afb30b93a
- https://git.kernel.org/stable/c/9edff632ca216169846f8a63a5a3dc467e239c7a
- https://git.kernel.org/stable/c/a17dc12bfed8868e6a86f3b45c16065a70641acb
- https://git.kernel.org/stable/c/d59cc66b702757e3c5a711e78a38583eac0c2738
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64235.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64235
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
