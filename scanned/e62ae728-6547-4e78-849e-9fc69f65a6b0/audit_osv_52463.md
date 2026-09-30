# [M] CVE-2021-47476

## Summary
Severity: Medium
Advisory: CVE-2021-47476
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47476
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

comedi: ni_usb6501: fix NULL-deref in command paths

The driver uses endpoint-sized USB transfer buffers but had no sanity
checks on the sizes. This can lead to zero-size-pointer dereferences or
overflowed transfer buffers in ni6501_port_command() and
ni6501_counter_command() if a (malicious) device has smaller max-packet
sizes than expected (or when doing descriptor fuzz testing).

Add the missing sanity checks to probe().

## References
- https://git.kernel.org/stable/c/58478143771b20ab219937b1c30a706590a59224
- https://git.kernel.org/stable/c/aa39738423503825625853b643b9e99d11c23816
- https://git.kernel.org/stable/c/b0156b7c9649d8f55a2ce3d3258509f1b2a181c3
- https://git.kernel.org/stable/c/d6a727a681a39ae4f73081a9bedb45d14f95bdd1
- https://git.kernel.org/stable/c/df7b1238f3b599a0b9284249772cdfd1ea83a632
- https://git.kernel.org/stable/c/ef143dc0c3defe56730ecd3a9de7b3e1d7e557c1
- https://git.kernel.org/stable/c/4a9d43cb5d5f39fa39fc1da438517004cc95f7ea
- https://git.kernel.org/stable/c/907767da8f3a925b060c740e0b5c92ea7dbec440
- https://git.kernel.org/stable/c/bc51111bf6e8e7b6cc94b133e4c291273a16acd1
