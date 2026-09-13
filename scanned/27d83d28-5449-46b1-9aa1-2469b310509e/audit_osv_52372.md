# [M] CVE-2021-47380

## Summary
Severity: Medium
Advisory: CVE-2021-47380
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47380
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: amd_sfh: Fix potential NULL pointer dereference

devm_add_action_or_reset() can suddenly invoke amd_mp2_pci_remove() at
registration that will cause NULL pointer dereference since
corresponding data is not initialized yet. The patch moves
initialization of data before devm_add_action_or_reset().

Found by Linux Driver Verification project (linuxtesting.org).

[jkosina@suse.cz: rebase]

## References
- https://git.kernel.org/stable/c/283e4bee701dfcd409dd293f19a268bb2bc8ff38
- https://git.kernel.org/stable/c/d46ef750ed58cbeeba2d9a55c99231c30a172764
