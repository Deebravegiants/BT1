# [M] CVE-2021-47236

## Summary
Severity: Medium
Advisory: CVE-2021-47236
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47236
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: cdc_eem: fix tx fixup skb leak

when usbnet transmit a skb, eem fixup it in eem_tx_fixup(),
if skb_copy_expand() failed, it return NULL,
usbnet_start_xmit() will have no chance to free original skb.

fix it by free orginal skb in eem_tx_fixup() first,
then check skb clone status, if failed, return NULL to usbnet.

## References
- https://git.kernel.org/stable/c/81de2ed06df8b5451e050fe6a318af3263dbff3f
- https://git.kernel.org/stable/c/b4f7a9fc9d094c0c4a66f2ad7c37b1dbe9e78f88
- https://git.kernel.org/stable/c/c3b26fdf1b32f91c7a3bc743384b4a298ab53ad7
- https://git.kernel.org/stable/c/f12554b0ff639e74612cc01b3b4a049e098d2d65
- https://git.kernel.org/stable/c/f4e6a7f19c82f39b1803e91c54718f0d7143767d
- https://git.kernel.org/stable/c/05b2b9f7d24b5663d9b47427fe1555bdafd3ea02
- https://git.kernel.org/stable/c/14184ec5c958b589ba934da7363a2877879204df
- https://git.kernel.org/stable/c/1bcacd6088d61c0ac6a990d87975600a81f3247e
