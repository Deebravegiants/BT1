# [M] CVE-2021-47527

## Summary
Severity: Medium
Advisory: CVE-2021-47527
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47527
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: core: fix transmit-buffer reset and memleak

Commit 761ed4a94582 ("tty: serial_core: convert uart_close to use
tty_port_close") converted serial core to use tty_port_close() but
failed to notice that the transmit buffer still needs to be freed on
final close.

Not freeing the transmit buffer means that the buffer is no longer
cleared on next open so that any ioctl() waiting for the buffer to drain
might wait indefinitely (e.g. on termios changes) or that stale data can
end up being transmitted in case tx is restarted.

Furthermore, the buffer of any port that has been opened would leak on
driver unbind.

Note that the port lock is held when clearing the buffer pointer due to
the ldisc race worked around by commit a5ba1d95e46e ("uart: fix race
between uart_put_char() and uart_shutdown()").

Also note that the tty-port shutdown() callback is not called for
console ports so it is not strictly necessary to free the buffer page
after releasing the lock (cf. d72402145ace ("tty/serial: do not free
trasnmit buffer page under port lock")).

## References
- https://git.kernel.org/stable/c/00de977f9e0aa9760d9a79d1e41ff780f74e3424
- https://git.kernel.org/stable/c/011f6c92b5bf6e1fbfdedc8b5232f64c1c493206
- https://git.kernel.org/stable/c/1179b168fa3f3a6aae3bd140000455a0e58457db
- https://git.kernel.org/stable/c/64e491c1634b73d3bddc081d08620bdc92ab2c12
- https://git.kernel.org/stable/c/c5da8aa441053958594f94254592bb41264bdfbf
- https://git.kernel.org/stable/c/e1722acf4f0d4d67b60f57e08ce16f8b66cd4b8f
- https://git.kernel.org/stable/c/e74d9663fd57640fc3394abb5c76fa95b9cc2f2e
