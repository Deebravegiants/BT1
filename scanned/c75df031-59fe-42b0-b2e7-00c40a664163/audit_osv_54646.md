# [M] CVE-2024-23848

## Summary
Severity: Medium
Advisory: CVE-2024-23848
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-23848
Type: osv

## Details
In the Linux kernel through 6.7.1, there is a use-after-free in cec_queue_msg_fh, related to drivers/media/cec/core/cec-adap.c and drivers/media/cec/core/cec-api.c.

## References
- https://lore.kernel.org/lkml/e9f42704-2f99-4f2c-ade5-f952e5fd53e5%40xs4all.nl/
