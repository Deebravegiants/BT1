# [H] wifi: ath12k: fix warning when unbinding

## Summary
Severity: High
Advisory: CVE-2024-53191
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53191
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix warning when unbinding

If there is an error during some initialization related to firmware,
the buffers dp->tx_ring[i].tx_status are released.
However this is released again when the device is unbinded (ath12k_pci),
and we get:
WARNING: CPU: 0 PID: 2098 at mm/slub.c:4689 free_large_kmalloc+0x4d/0x80
Call Trace:
free_large_kmalloc
ath12k_dp_free
ath12k_core_deinit
ath12k_pci_remove
...

The issue is always reproducible from a VM because the MSI addressing
initialization is failing.

In order to fix the issue, just set the buffers to NULL after releasing in
order to avoid the double free.

## References
- https://git.kernel.org/stable/c/223b546c6222d42147eff034433002ca5e2e7e09
- https://git.kernel.org/stable/c/90556b96338aa6037cd26dac857327fda7c19732
- https://git.kernel.org/stable/c/94c9100b600f05a36b33f9ed76dbd6fb0eb25386
- https://git.kernel.org/stable/c/ca68ce0d9f4bcd032fd1334441175ae399642a06
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53191.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53191
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
