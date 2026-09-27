# [H] Bluetooth: btintel_pcie: Allocate memory for driver private data

## Summary
Severity: High
Advisory: CVE-2024-46869
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-30
Source: https://osv.dev/vulnerability/CVE-2024-46869
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.12, >=6.11.0 <6.11.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btintel_pcie: Allocate memory for driver private data

Fix driver not allocating memory for struct btintel_data which is used
to store internal data.

## References
- https://git.kernel.org/stable/c/2b4545f08cc68d2fc835f5c490b36e0264750030
- https://git.kernel.org/stable/c/7ffaa200251871980af12e57649ad57c70bf0f43
- https://git.kernel.org/stable/c/fa9e1c1b1f389a8e6d987ac6cb3e2ba04f8ec875
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46869.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46869
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
