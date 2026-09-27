# [M] CVE-2021-47224

## Summary
Severity: Medium
Advisory: CVE-2021-47224
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47224
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ll_temac: Make sure to free skb when it is completely used

With the skb pointer piggy-backed on the TX BD, we have a simple and
efficient way to free the skb buffer when the frame has been transmitted.
But in order to avoid freeing the skb while there are still fragments from
the skb in use, we need to piggy-back on the TX BD of the skb, not the
first.

Without this, we are doing use-after-free on the DMA side, when the first
BD of a multi TX BD packet is seen as completed in xmit_done, and the
remaining BDs are still being processed.

## References
- https://git.kernel.org/stable/c/019ab7d044d0ebf97e1236bb8935b7809be92358
- https://git.kernel.org/stable/c/6aa32217a9a446275440ee8724b1ecaf1838df47
- https://git.kernel.org/stable/c/6d120ab4dc39a543c6b63361e1d0541c382900a3
- https://git.kernel.org/stable/c/e8afe05bd359ebe12a61dbdc94c06c00ea3e8d4b
