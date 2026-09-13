# [H] KVM: arm64: Fix shift-out-of-bounds bug

## Summary
Severity: High
Advisory: CVE-2024-50139
Ecosystem: Linux
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50139
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Fix shift-out-of-bounds bug

Fix a shift-out-of-bounds bug reported by UBSAN when running
VM with MTE enabled host kernel.

UBSAN: shift-out-of-bounds in arch/arm64/kvm/sys_regs.c:1988:14
shift exponent 33 is too large for 32-bit type 'int'
CPU: 26 UID: 0 PID: 7629 Comm: qemu-kvm Not tainted 6.12.0-rc2 #34
Hardware name: IEI NF5280R7/Mitchell MB, BIOS 00.00. 2024-10-12 09:28:54 10/14/2024
Call trace:
 dump_backtrace+0xa0/0x128
 show_stack+0x20/0x38
 dump_stack_lvl+0x74/0x90
 dump_stack+0x18/0x28
 __ubsan_handle_shift_out_of_bounds+0xf8/0x1e0
 reset_clidr+0x10c/0x1c8
 kvm_reset_sys_regs+0x50/0x1c8
 kvm_reset_vcpu+0xec/0x2b0
 __kvm_vcpu_set_target+0x84/0x158
 kvm_vcpu_set_target+0x138/0x168
 kvm_arch_vcpu_ioctl_vcpu_init+0x40/0x2b0
 kvm_arch_vcpu_ioctl+0x28c/0x4b8
 kvm_vcpu_ioctl+0x4bc/0x7a8
 __arm64_sys_ioctl+0xb4/0x100
 invoke_syscall+0x70/0x100
 el0_svc_common.constprop.0+0x48/0xf0
 do_el0_svc+0x24/0x38
 el0_svc+0x3c/0x158
 el0t_64_sync_handler+0x120/0x130
 el0t_64_sync+0x194/0x198

## References
- https://git.kernel.org/stable/c/04ed2ba07ce73f323052475fbd33d647aca3ff2e
- https://git.kernel.org/stable/c/4b9e11794d910aa55300debbac5f0adcc42c491a
- https://git.kernel.org/stable/c/c6c167afa090ea0451f91814e1318755a8fb8bb9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50139.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50139
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
