# [M] Bluetooth: hci_{ldisc,serdev}: check percpu_init_rwsem() failure

## Summary
Severity: Medium
Advisory: CVE-2022-50374
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50374
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_{ldisc,serdev}: check percpu_init_rwsem() failure

syzbot is reporting NULL pointer dereference at hci_uart_tty_close() [1],
for rcu_sync_enter() is called without rcu_sync_init() due to
hci_uart_tty_open() ignoring percpu_init_rwsem() failure.

While we are at it, fix that hci_uart_register_device() ignores
percpu_init_rwsem() failure and hci_uart_unregister_device() does not
call percpu_free_rwsem().

## References
- https://git.kernel.org/stable/c/3124d320c22f3f4388d9ac5c8f37eaad0cefd6b1
- https://git.kernel.org/stable/c/75b2c71ea581c7bb1303860d89366a42ad0506d2
- https://git.kernel.org/stable/c/98ce10f3f345e61fc6c83bff9cd11cda252b05ac
- https://git.kernel.org/stable/c/b8917dce2134739b39bc0a5648b18427f2cad569
- https://git.kernel.org/stable/c/d7cc0d51ffcbfd1caaa809fcf9cff05c46d0fb4d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50374.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50374
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
