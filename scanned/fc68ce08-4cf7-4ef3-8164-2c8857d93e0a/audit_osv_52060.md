# [M] CVE-2021-47020

## Summary
Severity: Medium
Advisory: CVE-2021-47020
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47020
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

soundwire: stream: fix memory leak in stream config error path

When stream config is failed, master runtime will release all
slave runtime in the slave_rt_list, but slave runtime is not
added to the list at this time. This patch frees slave runtime
in the config error path to fix the memory leak.

## References
- https://git.kernel.org/stable/c/2f17ac005b320c85d686088cfd4c2e7017912b88
- https://git.kernel.org/stable/c/342260fe821047c3d515e3d28085d73fbdce3e80
- https://git.kernel.org/stable/c/48f17f96a81763c7c8bf5500460a359b9939359f
- https://git.kernel.org/stable/c/7c468deae306d0cbbd539408c26cfec04c66159a
- https://git.kernel.org/stable/c/870533403ffa28ff63e173045fc5369365642002
- https://git.kernel.org/stable/c/effd2bd62b416f6629e18e3ce077c60de14cfdea
