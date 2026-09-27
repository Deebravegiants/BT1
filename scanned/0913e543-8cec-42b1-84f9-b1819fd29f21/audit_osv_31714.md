# [M] vsock/bpf: return early if transport is not assigned

## Summary
Severity: Medium
Advisory: CVE-2025-21670
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21670
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/bpf: return early if transport is not assigned

Some of the core functions can only be called if the transport
has been assigned.

As Michal reported, a socket might have the transport at NULL,
for example after a failed connect(), causing the following trace:

    BUG: kernel NULL pointer dereference, address: 00000000000000a0
    #PF: supervisor read access in kernel mode
    #PF: error_code(0x0000) - not-present page
    PGD 12faf8067 P4D 12faf8067 PUD 113670067 PMD 0
    Oops: Oops: 0000 [#1] PREEMPT SMP NOPTI
    CPU: 15 UID: 0 PID: 1198 Comm: a.out Not tainted 6.13.0-rc2+
    RIP: 0010:vsock_connectible_has_data+0x1f/0x40
    Call Trace:
     vsock_bpf_recvmsg+0xca/0x5e0
     sock_recvmsg+0xb9/0xc0
     __sys_recvfrom+0xb3/0x130
     __x64_sys_recvfrom+0x20/0x30
     do_syscall_64+0x93/0x180
     entry_SYSCALL_64_after_hwframe+0x76/0x7e

So we need to check the `vsk->transport` in vsock_bpf_recvmsg(),
especially for connected sockets (stream/seqpacket) as we already
do in __vsock_connectible_recvmsg().

## References
- https://git.kernel.org/stable/c/58e586c30d0b6f5dc0174a41026f2b0a48c9aab6
- https://git.kernel.org/stable/c/6771e1279dadf1d92a72e1465134257d9e6f2459
- https://git.kernel.org/stable/c/f6abafcd32f9cfc4b1a2f820ecea70773e26d423
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21670.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21670
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
