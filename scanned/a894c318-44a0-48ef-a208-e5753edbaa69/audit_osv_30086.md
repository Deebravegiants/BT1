# [H] net/mlx5: Fix error path in multi-packet WQE transmit

## Summary
Severity: High
Advisory: CVE-2024-50001
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50001
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Fix error path in multi-packet WQE transmit

Remove the erroneous unmap in case no DMA mapping was established

The multi-packet WQE transmit code attempts to obtain a DMA mapping for
the skb. This could fail, e.g. under memory pressure, when the IOMMU
driver just can't allocate more memory for page tables. While the code
tries to handle this in the path below the err_unmap label it erroneously
unmaps one entry from the sq's FIFO list of active mappings. Since the
current map attempt failed this unmap is removing some random DMA mapping
that might still be required. If the PCI function now presents that IOVA,
the IOMMU may assumes a rogue DMA access and e.g. on s390 puts the PCI
function in error state.

The erroneous behavior was seen in a stress-test environment that created
memory pressure.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/26fad69b34fcba80d5c7d9e651f628e6ac927754
- https://git.kernel.org/stable/c/2bcae12c795f32ddfbf8c80d1b5f1d3286341c32
- https://git.kernel.org/stable/c/8bb8c12fb5e2b1f03d603d493c92941676f109b5
- https://git.kernel.org/stable/c/ca36d6c1a49b6965c86dd528a73f38bc62d9c625
- https://git.kernel.org/stable/c/ce828b347cf1b3c1b12b091d02463c35ce5097f5
- https://git.kernel.org/stable/c/ecf310aaf256acbc8182189fe0aa1021c3ddef72
- https://git.kernel.org/stable/c/fc357e78176945ca7bcacf92ab794b9ccd41b4f4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50001.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50001
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
