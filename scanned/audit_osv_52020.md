# [H] CVE-2021-46973

## Summary
Severity: High
Advisory: CVE-2021-46973
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46973
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qrtr: Avoid potential use after free in MHI send

It is possible that the MHI ul_callback will be invoked immediately
following the queueing of the skb for transmission, leading to the
callback decrementing the refcount of the associated sk and freeing the
skb.

As such the dereference of skb and the increment of the sk refcount must
happen before the skb is queued, to avoid the skb to be used after free
and potentially the sk to drop its last refcount..

## References
- https://git.kernel.org/stable/c/03c649dee8b1eb5600212a249542a70f47a5ab40
- https://git.kernel.org/stable/c/47a017f33943278570c072bc71681809b2567b3a
- https://git.kernel.org/stable/c/48ec949ac979b4b42d740f67b6177797af834f80
- https://git.kernel.org/stable/c/ea474054c2cc6e1284604b21361f475c7cc8c0a0
