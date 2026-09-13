# [H] CVE-2021-47306

## Summary
Severity: High
Advisory: CVE-2021-47306
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47306
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fddi: fix UAF in fza_probe

fp is netdev private data and it cannot be
used after free_netdev() call. Using fp after free_netdev()
can cause UAF bug. Fix it by moving free_netdev() after error message.

TURBOchannel adapter")

## References
- https://git.kernel.org/stable/c/bdfbb51f7a437ae8ea91317a5c133ec13adf3c47
- https://git.kernel.org/stable/c/deb7178eb940e2c5caca1b1db084a69b2e59b4c9
- https://git.kernel.org/stable/c/f33605908a9b6063525e9f68e62d739948c5fccf
- https://git.kernel.org/stable/c/04b06716838bfc26742dbed3ae1d3697fe5317ee
