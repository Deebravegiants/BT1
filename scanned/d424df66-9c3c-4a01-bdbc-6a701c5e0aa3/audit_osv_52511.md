# [M] CVE-2021-47526

## Summary
Severity: Medium
Advisory: CVE-2021-47526
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47526
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: liteuart: Fix NULL pointer dereference in ->remove()

drvdata has to be set in _probe() - otherwise platform_get_drvdata()
causes null pointer dereference BUG in _remove().

## References
- https://git.kernel.org/stable/c/0f55f89d98c8b3e12b4f55f71c127a173e29557c
- https://git.kernel.org/stable/c/189c99c629bbf85916c02c153f904649cc0a9d7f
