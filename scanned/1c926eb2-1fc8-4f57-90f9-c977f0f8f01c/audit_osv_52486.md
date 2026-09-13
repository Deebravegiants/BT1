# [M] CVE-2021-47501

## Summary
Severity: Medium
Advisory: CVE-2021-47501
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47501
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: Fix NULL pointer dereference in i40e_dbg_dump_desc

When trying to dump VFs VSI RX/TX descriptors
using debugfs there was a crash
due to NULL pointer dereference in i40e_dbg_dump_desc.
Added a check to i40e_dbg_dump_desc that checks if
VSI type is correct for dumping RX/TX descriptors.

## References
- https://git.kernel.org/stable/c/23ec111bf3549aae37140330c31a16abfc172421
- https://git.kernel.org/stable/c/e5b7fb2198abc50058f1a29c395b004f76ab1c83
- https://git.kernel.org/stable/c/16431e442db248ecd8aa9457cf0a656f1885f56e
