# [H] vmxnet3: Fix packet corruption in vmxnet3_xdp_xmit_frame

## Summary
Severity: High
Advisory: CVE-2024-58099
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2024-58099
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

vmxnet3: Fix packet corruption in vmxnet3_xdp_xmit_frame

Andrew and Nikolay reported connectivity issues with Cilium's service
load-balancing in case of vmxnet3.

If a BPF program for native XDP adds an encapsulation header such as
IPIP and transmits the packet out the same interface, then in case
of vmxnet3 a corrupted packet is being sent and subsequently dropped
on the path.

vmxnet3_xdp_xmit_frame() which is called e.g. via vmxnet3_run_xdp()
through vmxnet3_xdp_xmit_back() calculates an incorrect DMA address:

  page = virt_to_page(xdpf->data);
  tbi->dma_addr = page_pool_get_dma_addr(page) +
                  VMXNET3_XDP_HEADROOM;
  dma_sync_single_for_device(&adapter->pdev->dev,
                             tbi->dma_addr, buf_size,
                             DMA_TO_DEVICE);

The above assumes a fixed offset (VMXNET3_XDP_HEADROOM), but the XDP
BPF program could have moved xdp->data. While the passed buf_size is
correct (xdpf->len), the dma_addr needs to have a dynamic offset which
can be calculated as xdpf->data - (void *)xdpf, that is, xdp->data -
xdp->data_hard_start.

## References
- https://git.kernel.org/stable/c/4678adf94da4a9e9683817b246b58ce15fb81782
- https://git.kernel.org/stable/c/59ba6cdadb9c26b606a365eb9c9b25eb2052622d
- https://git.kernel.org/stable/c/f82eb34fb59a8fb96c19f4f492c20eb774140bb5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58099.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
