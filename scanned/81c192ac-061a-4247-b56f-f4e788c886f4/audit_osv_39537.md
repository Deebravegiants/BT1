# [H] scsi: mpt3sas: Limit NVMe request size to 2 MiB

## Summary
Severity: High
Advisory: CVE-2026-46105
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46105
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpt3sas: Limit NVMe request size to 2 MiB

The HBA firmware reports NVMe MDTS values based on the underlying drive
capability. However, because the driver allocates a fixed 4K buffer for
the PRP list, accommodating at most 512 entries, the driver supports a
maximum I/O transfer size of 2 MiB.

Limit max_hw_sectors to the smaller of the reported MDTS and the 2 MiB
driver limit to prevent issuing oversized I/O that may lead to a kernel
oops.

## References
- https://git.kernel.org/stable/c/04631f55afc543d5431a2bdee7f6cc0f2c0debe7
- https://git.kernel.org/stable/c/45dcc815fc5539e88154315f36cbcb11d3a52fc2
- https://git.kernel.org/stable/c/e5f9824817c6358b9f9738bdb92dec9e4e794d3c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46105.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46105
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
