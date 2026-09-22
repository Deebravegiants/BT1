# [H] fprobe: Release rethook after the ftrace_ops is unregistered

## Summary
Severity: High
Advisory: CVE-2023-53557
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53557
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fprobe: Release rethook after the ftrace_ops is unregistered

While running bpf selftests it's possible to get following fault:

  general protection fault, probably for non-canonical address \
  0x6b6b6b6b6b6b6b6b: 0000 [#1] PREEMPT SMP DEBUG_PAGEALLOC NOPTI
  ...
  Call Trace:
   <TASK>
   fprobe_handler+0xc1/0x270
   ? __pfx_bpf_testmod_init+0x10/0x10
   ? __pfx_bpf_testmod_init+0x10/0x10
   ? bpf_fentry_test1+0x5/0x10
   ? bpf_fentry_test1+0x5/0x10
   ? bpf_testmod_init+0x22/0x80
   ? do_one_initcall+0x63/0x2e0
   ? rcu_is_watching+0xd/0x40
   ? kmalloc_trace+0xaf/0xc0
   ? do_init_module+0x60/0x250
   ? __do_sys_finit_module+0xac/0x120
   ? do_syscall_64+0x37/0x90
   ? entry_SYSCALL_64_after_hwframe+0x72/0xdc
   </TASK>

In unregister_fprobe function we can't release fp->rethook while it's
possible there are some of its users still running on another cpu.

Moving rethook_free call after fp->ops is unregistered with
unregister_ftrace_function call.

## References
- https://git.kernel.org/stable/c/03d63255a5783243c110aec5e6ae2f1475c3be76
- https://git.kernel.org/stable/c/5f81018753dfd4989e33ece1f0cb6b8aae498b82
- https://git.kernel.org/stable/c/ce3ec57faff559ccae1e0150c1f077eb2df648a4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53557.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53557
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
