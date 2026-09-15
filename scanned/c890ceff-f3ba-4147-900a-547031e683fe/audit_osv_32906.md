# [H] tty: serial: uartlite: register uart driver in init

## Summary
Severity: High
Advisory: CVE-2025-38262
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38262
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <5.4.296, >=5.5.0 <5.15.187, >=5.16.0 <6.1.143, >=6.2.0 <6.6.96, >=6.7.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: serial: uartlite: register uart driver in init

When two instances of uart devices are probing, a concurrency race can
occur. If one thread calls uart_register_driver function, which first
allocates and assigns memory to 'uart_state' member of uart_driver
structure, the other instance can bypass uart driver registration and
call ulite_assign. This calls uart_add_one_port, which expects the uart
driver to be fully initialized. This leads to a kernel panic due to a
null pointer dereference:

[    8.143581] BUG: kernel NULL pointer dereference, address: 00000000000002b8
[    8.156982] #PF: supervisor write access in kernel mode
[    8.156984] #PF: error_code(0x0002) - not-present page
[    8.156986] PGD 0 P4D 0
...
[    8.180668] RIP: 0010:mutex_lock+0x19/0x30
[    8.188624] Call Trace:
[    8.188629]  ? __die_body.cold+0x1a/0x1f
[    8.195260]  ? page_fault_oops+0x15c/0x290
[    8.209183]  ? __irq_resolve_mapping+0x47/0x80
[    8.209187]  ? exc_page_fault+0x64/0x140
[    8.209190]  ? asm_exc_page_fault+0x22/0x30
[    8.209196]  ? mutex_lock+0x19/0x30
[    8.223116]  uart_add_one_port+0x60/0x440
[    8.223122]  ? proc_tty_register_driver+0x43/0x50
[    8.223126]  ? tty_register_driver+0x1ca/0x1e0
[    8.246250]  ulite_probe+0x357/0x4b0 [uartlite]

To prevent it, move uart driver registration in to init function. This
will ensure that uart_driver is always registered when probe function
is called.

## References
- https://git.kernel.org/stable/c/5015eed450005bab6e5cb6810f7a62eab0434fc4
- https://git.kernel.org/stable/c/685d29f2c5057b32c7b1b46f2a7d303b926c8f72
- https://git.kernel.org/stable/c/6bd697b5fc39fd24e2aa418c7b7d14469f550a93
- https://git.kernel.org/stable/c/6db06aaea07bb7c8e33a425cf7b98bf29ee6056e
- https://git.kernel.org/stable/c/8e958d10dd0ce5ae674cce460db5c9ca3f25243b
- https://git.kernel.org/stable/c/9c905fdbba68a6d73d39a6b7de9b9f0d6c46df87
- https://git.kernel.org/stable/c/f5e4229d94792b40e750f30c92bcf7a3107c72ef
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38262.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38262
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
