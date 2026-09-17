# [H] CVE-2021-47669

## Summary
Severity: High
Advisory: CVE-2021-47669
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-17
Source: https://osv.dev/vulnerability/CVE-2021-47669
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: vxcan: vxcan_xmit: fix use after free bug

After calling netif_rx_ni(skb), dereferencing skb is unsafe.
Especially, the canfd_frame cfd which aliases skb memory is accessed
after the netif_rx_ni().

## References
- https://git.kernel.org/stable/c/6d6dcf2399cdd26f7f5426ca8dd8366b7f2ca105
- https://git.kernel.org/stable/c/75854cad5d80976f6ea0f0431f8cedd3bcc475cb
- https://git.kernel.org/stable/c/9b820875a32a3443d67bfd368e93038354e98052
- https://git.kernel.org/stable/c/a24476b37167816e6352ca1a2cf3769847774f70
- https://git.kernel.org/stable/c/e771a874076115df8bff27d325edfd2340e4ec69
