# [H] Avoid hw_desc array overrun in dw-axi-dmac

## Summary
Severity: High
Advisory: CVE-2024-40970
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40970
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.162, >=5.16.0 <6.1.96, >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Avoid hw_desc array overrun in dw-axi-dmac

I have a use case where nr_buffers = 3 and in which each descriptor is composed by 3
segments, resulting in the DMA channel descs_allocated to be 9. Since axi_desc_put()
handles the hw_desc considering the descs_allocated, this scenario would result in a
kernel panic (hw_desc array will be overrun).

To fix this, the proposal is to add a new member to the axi_dma_desc structure,
where we keep the number of allocated hw_descs (axi_desc_alloc()) and use it in
axi_desc_put() to handle the hw_desc array correctly.

Additionally I propose to remove the axi_chan_start_first_queued() call after completing
the transfer, since it was identified that unbalance can occur (started descriptors can
be interrupted and transfer ignored due to DMA channel not being enabled).

## References
- https://git.kernel.org/stable/c/333e11bf47fa8d477db90e2900b1ed3c9ae9b697
- https://git.kernel.org/stable/c/7c3bb96a20cd8db3b8824b2ff08b6cde4505c7e5
- https://git.kernel.org/stable/c/9004784e8d68bcd1ac1376407ba296fa28f04dbe
- https://git.kernel.org/stable/c/dd42570018f5962c10f215ad9c21274ed5d3541e
- https://git.kernel.org/stable/c/e151ae1ee065cf4b8ce4394ddb9d9c8df6370c66
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40970.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40970
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
