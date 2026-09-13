# [H] media: ti: j721e-csi2rx: Fix races while restarting DMA

## Summary
Severity: High
Advisory: CVE-2024-32936
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-32936
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: ti: j721e-csi2rx: Fix races while restarting DMA

After the frame is submitted to DMA, it may happen that the submitted
list is not updated soon enough, and the DMA callback is triggered
before that.

This can lead to kernel crashes, so move everything in a single
lock/unlock section to prevent such races.

## References
- https://git.kernel.org/stable/c/80a8b92950f8ee96582dba6187e3c2deca3569ea
- https://git.kernel.org/stable/c/ad79c9ecea5baa7b4f19677e4b1c881ed89b0c3b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32936.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32936
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
