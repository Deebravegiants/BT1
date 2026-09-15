# [M] CVE-2021-47367

## Summary
Severity: Medium
Advisory: CVE-2021-47367
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47367
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-net: fix pages leaking when building skb in big mode

We try to use build_skb() if we had sufficient tailroom. But we forget
to release the unused pages chained via private in big mode which will
leak pages. Fixing this by release the pages after building the skb in
big mode.

## References
- https://git.kernel.org/stable/c/afd92d82c9d715fb97565408755acad81573591a
- https://git.kernel.org/stable/c/f020bb63b5d2e5576acadd10e158fe3b04af67ba
