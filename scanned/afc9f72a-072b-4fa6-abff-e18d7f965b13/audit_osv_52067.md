# [M] CVE-2021-47033

## Summary
Severity: Medium
Advisory: CVE-2021-47033
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47033
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: mt7615: fix tx skb dma unmap

The first pointer in the txp needs to be unmapped as well, otherwise it will
leak DMA mapping entries

## References
- https://git.kernel.org/stable/c/75bc5f779a7664d1fc19cb915039439c6e58bb94
- https://git.kernel.org/stable/c/821ae236ccea989a1fcc6abfc4d5b74ad4ba39d2
- https://git.kernel.org/stable/c/a025277a80add18c33d01042525a74fe5b875f25
- https://git.kernel.org/stable/c/ebee7885bb12a8fe2c2f9bac87dbd87a05b645f9
