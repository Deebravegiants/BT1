# [M] CVE-2021-47032

## Summary
Severity: Medium
Advisory: CVE-2021-47032
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47032
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: mt7915: fix tx skb dma unmap

The first pointer in the txp needs to be unmapped as well, otherwise it will
leak DMA mapping entries

## References
- https://git.kernel.org/stable/c/4a9dcd6efb2a268fc5707dcfb3b0c412975c4462
- https://git.kernel.org/stable/c/4e7914ce23306b28d377ec395e00e5fde0e6f96e
- https://git.kernel.org/stable/c/7dcf3c04f0aca746517a77433b33d40868ca4749
- https://git.kernel.org/stable/c/e2cdc9cb33c5963efe1a7c022753386f9463d1b7
