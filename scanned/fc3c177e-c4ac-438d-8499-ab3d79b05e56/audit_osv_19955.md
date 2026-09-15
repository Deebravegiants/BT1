# [H] CVE-2021-28361

## Summary
Severity: High
Advisory: CVE-2021-28361
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-13
Source: https://osv.dev/vulnerability/CVE-2021-28361
Type: osv

## Details
An issue was discovered in Storage Performance Development Kit (SPDK) before 20.01.01. If a PDU is sent to the iSCSI target with a zero length (but data is expected), the iSCSI target can crash with a NULL pointer dereference.

## References
- https://github.com/spdk/spdk/releases/tag/v21.01.1
