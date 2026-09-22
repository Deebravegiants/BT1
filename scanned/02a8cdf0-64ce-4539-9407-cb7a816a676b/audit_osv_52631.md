# [H] CVE-2021-47668

## Summary
Severity: High
Advisory: CVE-2021-47668
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-17
Source: https://osv.dev/vulnerability/CVE-2021-47668
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: dev: can_restart: fix use after free bug

After calling netif_rx_ni(skb), dereferencing skb is unsafe.
Especially, the can_frame cf which aliases skb memory is accessed
after the netif_rx_ni() in:
      stats->rx_bytes += cf->len;

Reordering the lines solves the issue.

## References
- https://git.kernel.org/stable/c/03f16c5075b22c8902d2af739969e878b0879c94
- https://git.kernel.org/stable/c/08ab951787098ae0b6c0364aeea7a8138226f234
- https://git.kernel.org/stable/c/260925a0b7d2da5449f8ecfd02c1405e0c8a45b8
- https://git.kernel.org/stable/c/593c072b7b3c4d7044416eb039d9ad706bedd67a
- https://git.kernel.org/stable/c/92668d28c7e6a7a2ba07df287669ffcdf650c421
- https://git.kernel.org/stable/c/ac48ef15826e83f4206c47add61072e8fc76d328
- https://git.kernel.org/stable/c/bbc6847b9b8978b520f62fbc7c68c54ef0f8d282
