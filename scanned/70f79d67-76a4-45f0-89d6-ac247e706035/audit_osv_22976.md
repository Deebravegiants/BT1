# [H] CVE-2022-41858

## Summary
Severity: High
Advisory: CVE-2022-41858
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2022-41858
Type: osv

## Details
A flaw was found in the Linux kernel. A NULL pointer dereference may occur while a slip driver is in progress to detach in sl_tx_timeout in drivers/net/slip/slip.c. This issue could allow an attacker to crash the system or leak internal kernel information.

## References
- https://security.netapp.com/advisory/ntap-20230223-0006/
- https://github.com/torvalds/linux/commit/ec4eb8a86ade4d22633e1da2a7d85a846b7d1798
