# [M] CVE-2021-47330

## Summary
Severity: Medium
Advisory: CVE-2021-47330
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47330
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: serial: 8250: serial_cs: Fix a memory leak in error handling path

In the probe function, if the final 'serial_config()' fails, 'info' is
leaking.

Add a resource handling path to free this memory.

## References
- https://git.kernel.org/stable/c/34f4590f5ec9859ea9136249f528173d150bd584
- https://git.kernel.org/stable/c/7a80f71601af015856a0aeb1e3c294037ac3dd32
- https://git.kernel.org/stable/c/c39cf4df19acf0133fa284a8cd83fad42cd13cc2
- https://git.kernel.org/stable/c/ee16bed959862a6de2913f71a04cb563d7237b67
- https://git.kernel.org/stable/c/331f5923fce4f45b8170ccf06c529e8eb28f37bc
- https://git.kernel.org/stable/c/b2ef1f5de40342de44fc5355321595f91774dab5
- https://git.kernel.org/stable/c/b5a2799cd62ed30c81b22c23028d9ee374e2138c
- https://git.kernel.org/stable/c/cddee5c287e26f6b2ba5c0ffdfc3a846f2f10461
- https://git.kernel.org/stable/c/fad92b11047a748c996ebd6cfb164a63814eeb2e
