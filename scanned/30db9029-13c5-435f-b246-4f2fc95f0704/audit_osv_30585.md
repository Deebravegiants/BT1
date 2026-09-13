# [H] wifi: ath12k: fix crash when unbinding

## Summary
Severity: High
Advisory: CVE-2024-53188
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53188
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix crash when unbinding

If there is an error during some initialization related to firmware,
the function ath12k_dp_cc_cleanup is called to release resources.
However this is released again when the device is unbinded (ath12k_pci),
and we get:
BUG: kernel NULL pointer dereference, address: 0000000000000020
at RIP: 0010:ath12k_dp_cc_cleanup.part.0+0xb6/0x500 [ath12k]
Call Trace:
ath12k_dp_cc_cleanup
ath12k_dp_free
ath12k_core_deinit
ath12k_pci_remove
...

The issue is always reproducible from a VM because the MSI addressing
initialization is failing.

In order to fix the issue, just set to NULL the released structure in
ath12k_dp_cc_cleanup at the end.

## References
- https://git.kernel.org/stable/c/1304446f67863385dc4c914b6e0194f6664ee764
- https://git.kernel.org/stable/c/2eec88c0fa63f8ad35704a8c9df0b5bd8694fcda
- https://git.kernel.org/stable/c/488d2959c28621e52b3cce118a813a4bc18bb3d1
- https://git.kernel.org/stable/c/81da9c0854545c3188ca2a09afe7cb65f9c012b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53188.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53188
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
