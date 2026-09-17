# [H] drm/vmwgfx: Fix prime with external buffers

## Summary
Severity: High
Advisory: CVE-2024-46709
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46709
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.49, >=6.7.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Fix prime with external buffers

Make sure that for external buffers mapping goes through the dma_buf
interface instead of trying to access pages directly.

External buffers might not provide direct access to readable/writable
pages so to make sure the bo's created from external dma_bufs can be
read dma_buf interface has to be used.

Fixes crashes in IGT's kms_prime with vgem. Regular desktop usage won't
trigger this due to the fact that virtual machines will not have
multiple GPUs but it enables better test coverage in IGT.

## References
- https://git.kernel.org/stable/c/50f1199250912568606b3778dc56646c10cb7b04
- https://git.kernel.org/stable/c/5c12391ee1ab59cb2f3be3f1f5e6d0fc0c2dc854
- https://git.kernel.org/stable/c/9a9716bbbf3dd6b6cbefba3abcc89af8b72631f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46709.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46709
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
