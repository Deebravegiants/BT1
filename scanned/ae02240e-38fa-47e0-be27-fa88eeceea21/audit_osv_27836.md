# [H] bpf: Reject variable offset alu on PTR_TO_FLOW_KEYS

## Summary
Severity: High
Advisory: CVE-2024-26589
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2024-26589
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reject variable offset alu on PTR_TO_FLOW_KEYS

For PTR_TO_FLOW_KEYS, check_flow_keys_access() only uses fixed off
for validation. However, variable offset ptr alu is not prohibited
for this ptr kind. So the variable offset is not checked.

The following prog is accepted:

  func#0 @0
  0: R1=ctx() R10=fp0
  0: (bf) r6 = r1                       ; R1=ctx() R6_w=ctx()
  1: (79) r7 = *(u64 *)(r6 +144)        ; R6_w=ctx() R7_w=flow_keys()
  2: (b7) r8 = 1024                     ; R8_w=1024
  3: (37) r8 /= 1                       ; R8_w=scalar()
  4: (57) r8 &= 1024                    ; R8_w=scalar(smin=smin32=0,
  smax=umax=smax32=umax32=1024,var_off=(0x0; 0x400))
  5: (0f) r7 += r8
  mark_precise: frame0: last_idx 5 first_idx 0 subseq_idx -1
  mark_precise: frame0: regs=r8 stack= before 4: (57) r8 &= 1024
  mark_precise: frame0: regs=r8 stack= before 3: (37) r8 /= 1
  mark_precise: frame0: regs=r8 stack= before 2: (b7) r8 = 1024
  6: R7_w=flow_keys(smin=smin32=0,smax=umax=smax32=umax32=1024,var_off
  =(0x0; 0x400)) R8_w=scalar(smin=smin32=0,smax=umax=smax32=umax32=1024,
  var_off=(0x0; 0x400))
  6: (79) r0 = *(u64 *)(r7 +0)          ; R0_w=scalar()
  7: (95) exit

This prog loads flow_keys to r7, and adds the variable offset r8
to r7, and finally causes out-of-bounds access:

  BUG: unable to handle page fault for address: ffffc90014c80038
  [...]
  Call Trace:
   <TASK>
   bpf_dispatcher_nop_func include/linux/bpf.h:1231 [inline]
   __bpf_prog_run include/linux/filter.h:651 [inline]
   bpf_prog_run include/linux/filter.h:658 [inline]
   bpf_prog_run_pin_on_cpu include/linux/filter.h:675 [inline]
   bpf_flow_dissect+0x15f/0x350 net/core/flow_dissector.c:991
   bpf_prog_test_run_flow_dissector+0x39d/0x620 net/bpf/test_run.c:1359
   bpf_prog_test_run kernel/bpf/syscall.c:4107 [inline]
   __sys_bpf+0xf8f/0x4560 kernel/bpf/syscall.c:5475
   __do_sys_bpf kernel/bpf/syscall.c:5561 [inline]
   __se_sys_bpf kernel/bpf/syscall.c:5559 [inline]
   __x64_sys_bpf+0x73/0xb0 kernel/bpf/syscall.c:5559
   do_syscall_x64 arch/x86/entry/common.c:52 [inline]
   do_syscall_64+0x3f/0x110 arch/x86/entry/common.c:83
   entry_SYSCALL_64_after_hwframe+0x63/0x6b

Fix this by rejecting ptr alu with variable offset on flow_keys.
Applying the patch rejects the program with "R7 pointer arithmetic
on flow_keys prohibited".

## References
- https://git.kernel.org/stable/c/1b500d5d6cecf98dd6ca88bc9e7ae1783c83e6d3
- https://git.kernel.org/stable/c/22c7fa171a02d310e3a3f6ed46a698ca8a0060ed
- https://git.kernel.org/stable/c/29ffa63f21bcdcef3e36b03cccf9d0cd031f6ab0
- https://git.kernel.org/stable/c/4108b86e324da42f7ed425bd71632fd844300dc8
- https://git.kernel.org/stable/c/e8d3872b617c21100c5ee4f64e513997a68c2e3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26589.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26589
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
