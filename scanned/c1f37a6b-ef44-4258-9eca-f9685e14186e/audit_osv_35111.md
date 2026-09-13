# [H] locking/spinlock/debug: Fix data-race in do_raw_write_lock

## Summary
Severity: High
Advisory: CVE-2025-68336
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2025-68336
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.62, >=6.13.0 <6.17.12, >=6.18.0 <6.18.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

locking/spinlock/debug: Fix data-race in do_raw_write_lock

KCSAN reports:

BUG: KCSAN: data-race in do_raw_write_lock / do_raw_write_lock

write (marked) to 0xffff800009cf504c of 4 bytes by task 1102 on cpu 1:
 do_raw_write_lock+0x120/0x204
 _raw_write_lock_irq
 do_exit
 call_usermodehelper_exec_async
 ret_from_fork

read to 0xffff800009cf504c of 4 bytes by task 1103 on cpu 0:
 do_raw_write_lock+0x88/0x204
 _raw_write_lock_irq
 do_exit
 call_usermodehelper_exec_async
 ret_from_fork

value changed: 0xffffffff -> 0x00000001

Reported by Kernel Concurrency Sanitizer on:
CPU: 0 PID: 1103 Comm: kworker/u4:1 6.1.111

Commit 1a365e822372 ("locking/spinlock/debug: Fix various data races") has
adressed most of these races, but seems to be not consistent/not complete.

>From do_raw_write_lock() only debug_write_lock_after() part has been
converted to WRITE_ONCE(), but not debug_write_lock_before() part.
Do it now.

## References
- https://git.kernel.org/stable/c/16b3590c0e1e615757dade098c8fbc0d4f040c76
- https://git.kernel.org/stable/c/396a9270a7b90886be501611b13aa636f2e8c703
- https://git.kernel.org/stable/c/39d2ef113416f1a4205b03fb0aa2e428d1412c77
- https://git.kernel.org/stable/c/8e5b2cf10844402054b52b489b525dc30cc16908
- https://git.kernel.org/stable/c/93bd23524d63deb80fb85beb2e43fafeb1043d0f
- https://git.kernel.org/stable/c/b163a5e8c703201c905d6ec7920ed79d167e8442
- https://git.kernel.org/stable/c/c14ecb555c3ee80eeb030a4e46d00e679537f03a
- https://git.kernel.org/stable/c/c228cb699a07a5f2d596d186bc5c314c99bb8bbf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68336.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68336
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
