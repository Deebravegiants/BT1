# [H] dmaengine: dw-edma: eDMA: Add sync read before starting the DMA transfer in remote setup

## Summary
Severity: High
Advisory: CVE-2024-27408
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27408
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.6.21, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: dw-edma: eDMA: Add sync read before starting the DMA transfer in remote setup

The Linked list element and pointer are not stored in the same memory as
the eDMA controller register. If the doorbell register is toggled before
the full write of the linked list a race condition error will occur.
In remote setup we can only use a readl to the memory to assure the full
write has occurred.

## References
- https://git.kernel.org/stable/c/bbcc1c83f343e580c3aa1f2a8593343bf7b55bba
- https://git.kernel.org/stable/c/d24fe6d5a1cfdddb7a9ef56736ec501c4d0a5fd3
- https://git.kernel.org/stable/c/f396b4df27cfe01a99f4b41f584c49e56477be3a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27408.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
