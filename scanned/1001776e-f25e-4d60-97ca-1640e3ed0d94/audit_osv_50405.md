# [M] CVE-2020-15437

## Summary
Severity: Medium
Advisory: CVE-2020-15437
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2020-15437
Type: osv

## Details
The Linux kernel before version 5.8 is vulnerable to a NULL pointer dereference in drivers/tty/serial/8250/8250_core.c:serial8250_isa_init_ports() that allows local users to cause a denial of service by using the p->serial_in pointer which uninitialized.

## References
- https://lkml.org/lkml/2020/7/21/80
