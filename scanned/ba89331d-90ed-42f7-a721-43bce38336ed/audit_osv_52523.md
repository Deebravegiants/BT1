# [M] CVE-2021-47539

## Summary
Severity: Medium
Advisory: CVE-2021-47539
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47539
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix rxrpc_peer leak in rxrpc_look_up_bundle()

Need to call rxrpc_put_peer() for bundle candidate before kfree() as it
holds a ref to rxrpc_peer.

[DH: v2: Changed to abstract out the bundle freeing code into a function]

## References
- https://git.kernel.org/stable/c/35b40f724c4ef0f683d94dab3af9ab38261d782b
- https://git.kernel.org/stable/c/bc97458620e38961af9505cc060ad4cf5c9e4af7
- https://git.kernel.org/stable/c/ca77fba821351190777b236ce749d7c4d353102e
