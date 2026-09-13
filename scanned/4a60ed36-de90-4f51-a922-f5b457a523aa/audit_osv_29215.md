# [H] dmaengine: xilinx: xdma: Fix data synchronisation in xdma_channel_isr()

## Summary
Severity: High
Advisory: CVE-2024-40986
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40986
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: xilinx: xdma: Fix data synchronisation in xdma_channel_isr()

Requests the vchan lock before using xdma->stop_request.

## References
- https://git.kernel.org/stable/c/462237d2d93fc9e9221d1cf9f773954d27da83c0
- https://git.kernel.org/stable/c/8e1f54e4a3f3207c9dc68bb5000603b75802e7f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40986.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40986
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
