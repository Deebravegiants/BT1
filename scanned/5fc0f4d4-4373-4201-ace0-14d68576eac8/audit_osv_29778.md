# [H] dmaengine: altera-msgdma: properly free descriptor in msgdma_free_descriptor

## Summary
Severity: High
Advisory: CVE-2024-46716
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46716
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <6.1.109, >=6.2.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: altera-msgdma: properly free descriptor in msgdma_free_descriptor

Remove list_del call in msgdma_chan_desc_cleanup, this should be the role
of msgdma_free_descriptor. In consequence replace list_add_tail with
list_move_tail in msgdma_free_descriptor.

This fixes the path:
   msgdma_free_chan_resources -> msgdma_free_descriptors ->
   msgdma_free_desc_list -> msgdma_free_descriptor

which does not correctly free the descriptors as first nodes were not
removed from the list.

## References
- https://git.kernel.org/stable/c/20bf2920a869f9dbda0ef8c94c87d1901a64a716
- https://git.kernel.org/stable/c/54e4ada1a4206f878e345ae01cf37347d803d1b1
- https://git.kernel.org/stable/c/a3480e59fdbe5585d2d1eff0bed7671583acf725
- https://git.kernel.org/stable/c/db67686676c7becc1910bf1d6d51505876821863
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46716.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46716
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
