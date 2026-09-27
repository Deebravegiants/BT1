# [M] nvme-pci: fix freeing of the HMB descriptor table

## Summary
Severity: Medium
Advisory: CVE-2024-56756
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56756
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-pci: fix freeing of the HMB descriptor table

The HMB descriptor table is sized to the maximum number of descriptors
that could be used for a given device, but __nvme_alloc_host_mem could
break out of the loop earlier on memory allocation failure and end up
using less descriptors than planned for, which leads to an incorrect
size passed to dma_free_coherent.

In practice this was not showing up because the number of descriptors
tends to be low and the dma coherent allocator always allocates and
frees at least a page.

## References
- https://git.kernel.org/stable/c/3c2fb1ca8086eb139b2a551358137525ae8e0d7a
- https://git.kernel.org/stable/c/452f9ddd12bebc04cef741e8ba3806bf0e1fd015
- https://git.kernel.org/stable/c/582d9ed999b004fb1d415ecbfa86d4d8df455269
- https://git.kernel.org/stable/c/6d0f599db73b099aa724a12736369c4d4d92849d
- https://git.kernel.org/stable/c/869cf50b9c9d1059f5223f79ef68fc0bc6210095
- https://git.kernel.org/stable/c/ac22240540e0c5230d8c4138e3778420b712716a
- https://git.kernel.org/stable/c/cee3bff51a35cab1c5d842d409a7b11caefe2386
- https://git.kernel.org/stable/c/fb96d5cfa97a7363245b3dd523f475b04296d87b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56756.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56756
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
