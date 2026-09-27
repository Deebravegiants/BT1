# [H] bpf, sockmap: Fix repeated calls to sock_put() when msg has more_data

## Summary
Severity: High
Advisory: CVE-2022-50536
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2022-50536
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.15.0 <6.0.16, >=5.16.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Fix repeated calls to sock_put() when msg has more_data

In tcp_bpf_send_verdict() redirection, the eval variable is assigned to
__SK_REDIRECT after the apply_bytes data is sent, if msg has more_data,
sock_put() will be called multiple times.

We should reset the eval variable to __SK_NONE every time more_data
starts.

This causes:

IPv4: Attempt to release TCP socket in state 1 00000000b4c925d7
------------[ cut here ]------------
refcount_t: addition on 0; use-after-free.
WARNING: CPU: 5 PID: 4482 at lib/refcount.c:25 refcount_warn_saturate+0x7d/0x110
Modules linked in:
CPU: 5 PID: 4482 Comm: sockhash_bypass Kdump: loaded Not tainted 6.0.0 #1
Hardware name: Red Hat KVM, BIOS 1.11.0-2.el7 04/01/2014
Call Trace:
 <TASK>
 __tcp_transmit_skb+0xa1b/0xb90
 ? __alloc_skb+0x8c/0x1a0
 ? __kmalloc_node_track_caller+0x184/0x320
 tcp_write_xmit+0x22a/0x1110
 __tcp_push_pending_frames+0x32/0xf0
 do_tcp_sendpages+0x62d/0x640
 tcp_bpf_push+0xae/0x2c0
 tcp_bpf_sendmsg_redir+0x260/0x410
 ? preempt_count_add+0x70/0xa0
 tcp_bpf_send_verdict+0x386/0x4b0
 tcp_bpf_sendmsg+0x21b/0x3b0
 sock_sendmsg+0x58/0x70
 __sys_sendto+0xfa/0x170
 ? xfd_validate_state+0x1d/0x80
 ? switch_fpu_return+0x59/0xe0
 __x64_sys_sendto+0x24/0x30
 do_syscall_64+0x37/0x90
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

## References
- https://git.kernel.org/stable/c/113236e8f49f262f318c00ebb14b15f4834e87c1
- https://git.kernel.org/stable/c/28e4a763cd4a2b1a78852216ef4bd7df3a05cec6
- https://git.kernel.org/stable/c/578a7628b838a3ac8ad61deaab5a816ff032ac13
- https://git.kernel.org/stable/c/7508b9f4daac4ec7dfe0b6fb2d688b1c1c105e10
- https://git.kernel.org/stable/c/7a9841ca025275b5b0edfb0b618934abb6ceec15
- https://git.kernel.org/stable/c/8786bde11a4f31b63b3036731df0b47337a7a245
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50536.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50536
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
