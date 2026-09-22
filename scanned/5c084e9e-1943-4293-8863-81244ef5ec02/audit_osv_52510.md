# [H] CVE-2021-47525

## Summary
Severity: High
Advisory: CVE-2021-47525
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47525
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: liteuart: fix use-after-free and memleak on unbind

Deregister the port when unbinding the driver to prevent it from being
used after releasing the driver data and leaking memory allocated by
serial core.

## References
- https://git.kernel.org/stable/c/05f929b395dec8957b636ff14e66b277ed022ed9
- https://git.kernel.org/stable/c/602824cf9aa9db8830ffe5cfb2cd54365cada4fe
