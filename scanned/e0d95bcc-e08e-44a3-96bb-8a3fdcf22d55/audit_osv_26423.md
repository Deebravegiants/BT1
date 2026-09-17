# [H] serial: 8250: Reinit port->pm on port specific driver unbind

## Summary
Severity: High
Advisory: CVE-2023-53176
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53176
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: 8250: Reinit port->pm on port specific driver unbind

When we unbind a serial port hardware specific 8250 driver, the generic
serial8250 driver takes over the port. After that we see an oops about 10
seconds later. This can produce the following at least on some TI SoCs:

Unhandled fault: imprecise external abort (0x1406)
Internal error: : 1406 [#1] SMP ARM

Turns out that we may still have the serial port hardware specific driver
port->pm in use, and serial8250_pm() tries to call it after the port
specific driver is gone:

serial8250_pm [8250_base] from uart_change_pm+0x54/0x8c [serial_base]
uart_change_pm [serial_base] from uart_hangup+0x154/0x198 [serial_base]
uart_hangup [serial_base] from __tty_hangup.part.0+0x328/0x37c
__tty_hangup.part.0 from disassociate_ctty+0x154/0x20c
disassociate_ctty from do_exit+0x744/0xaac
do_exit from do_group_exit+0x40/0x8c
do_group_exit from __wake_up_parent+0x0/0x1c

Let's fix the issue by calling serial8250_set_defaults() in
serial8250_unregister_port(). This will set the port back to using
the serial8250 default functions, and sets the port->pm to point to
serial8250_pm.

## References
- https://git.kernel.org/stable/c/04e82793f068d2f0ffe62fcea03d007a8cdc16a7
- https://git.kernel.org/stable/c/1ba5594739d858e524ff0f398ee1ebfe0a8b9d41
- https://git.kernel.org/stable/c/2c86a1305c1406f45ea780d06953c484ea1d9e6e
- https://git.kernel.org/stable/c/490bf37eaabb0a857ed1ae8e75d8854e41662f1c
- https://git.kernel.org/stable/c/8e596aed5f2f98cf3e6e98d6fe1d689f4a319308
- https://git.kernel.org/stable/c/af4d6dbb1a92ea424ad1ba1d0c88c7fa2345d872
- https://git.kernel.org/stable/c/c9e080c3005fd183c56ff8f4d75edb5da0765d2c
- https://git.kernel.org/stable/c/d5cd2928d31042a7c0a01464f9a8d95be736421d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53176.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53176
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
