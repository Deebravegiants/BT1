# [M] CVE-2021-47270

## Summary
Severity: Medium
Advisory: CVE-2021-47270
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47270
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: fix various gadgets null ptr deref on 10gbps cabling.

This avoids a null pointer dereference in
f_{ecm,eem,hid,loopback,printer,rndis,serial,sourcesink,subset,tcm}
by simply reusing the 5gbps config for 10gbps.

## References
- https://git.kernel.org/stable/c/8cd5f45c1b769e3e9e0f4325dd08b6c3749dc7ee
- https://git.kernel.org/stable/c/90c4d05780d47e14a50e11a7f17373104cd47d25
- https://git.kernel.org/stable/c/b4903f7fdc484628d0b8022daf86e2439d3ab4db
- https://git.kernel.org/stable/c/beb1e67a5ca8d69703c776db9000527f44c0c93c
- https://git.kernel.org/stable/c/f17aae7c4009160f0630a91842a281773976a5bc
- https://git.kernel.org/stable/c/10770d2ac0094b053c8897d96d7b2737cd72f7c5
- https://git.kernel.org/stable/c/4b289a0f3033f465b4fd51ba995251a7867a2aa2
