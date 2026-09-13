# [H] KVM: x86/mmu: make apf token non-zero to fix bug

## Summary
Severity: High
Advisory: CVE-2022-48943
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2022-48943
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.103, >=5.11.0 <5.15.26, >=5.16.0 <5.16.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86/mmu: make apf token non-zero to fix bug

In current async pagefault logic, when a page is ready, KVM relies on
kvm_arch_can_dequeue_async_page_present() to determine whether to deliver
a READY event to the Guest. This function test token value of struct
kvm_vcpu_pv_apf_data, which must be reset to zero by Guest kernel when a
READY event is finished by Guest. If value is zero meaning that a READY
event is done, so the KVM can deliver another.
But the kvm_arch_setup_async_pf() may produce a valid token with zero
value, which is confused with previous mention and may lead the loss of
this READY event.

This bug may cause task blocked forever in Guest:
 INFO: task stress:7532 blocked for more than 1254 seconds.
       Not tainted 5.10.0 #16
 "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
 task:stress          state:D stack:    0 pid: 7532 ppid:  1409
 flags:0x00000080
 Call Trace:
  __schedule+0x1e7/0x650
  schedule+0x46/0xb0
  kvm_async_pf_task_wait_schedule+0xad/0xe0
  ? exit_to_user_mode_prepare+0x60/0x70
  __kvm_handle_async_pf+0x4f/0xb0
  ? asm_exc_page_fault+0x8/0x30
  exc_page_fault+0x6f/0x110
  ? asm_exc_page_fault+0x8/0x30
  asm_exc_page_fault+0x1e/0x30
 RIP: 0033:0x402d00
 RSP: 002b:00007ffd31912500 EFLAGS: 00010206
 RAX: 0000000000071000 RBX: ffffffffffffffff RCX: 00000000021a32b0
 RDX: 000000000007d011 RSI: 000000000007d000 RDI: 00000000021262b0
 RBP: 00000000021262b0 R08: 0000000000000003 R09: 0000000000000086
 R10: 00000000000000eb R11: 00007fefbdf2baa0 R12: 0000000000000000
 R13: 0000000000000002 R14: 000000000007d000 R15: 0000000000001000

## References
- https://git.kernel.org/stable/c/4c3644b6c96c5daa5149e5abddc07234eea47c7c
- https://git.kernel.org/stable/c/62040f5cd7d937de547836e747b6aa8212fec573
- https://git.kernel.org/stable/c/6f3c1fc53d86d580d8d6d749c4af23705e4f6f79
- https://git.kernel.org/stable/c/72fdfc75d4217b32363cc80def3de2cb3fef3f02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48943.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48943
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
