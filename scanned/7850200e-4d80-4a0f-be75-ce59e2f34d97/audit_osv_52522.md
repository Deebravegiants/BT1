# [M] CVE-2021-47538

## Summary
Severity: Medium
Advisory: CVE-2021-47538
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47538
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix rxrpc_local leak in rxrpc_lookup_peer()

Need to call rxrpc_put_local() for peer candidate before kfree() as it
holds a ref to rxrpc_local.

[DH: v2: Changed to abstract the peer freeing code out into a function]

## References
- https://git.kernel.org/stable/c/3e70e3a72d80b16094faccbe438cd53761c3503a
- https://git.kernel.org/stable/c/60f0b9c42cb80833a03ca57c1c8b078d716e71d1
- https://git.kernel.org/stable/c/913c24af2d13a3fd304462916ee98e298d56bdce
- https://git.kernel.org/stable/c/9469273e616ca8f1b6e3773c5019f21b4c8d828c
- https://git.kernel.org/stable/c/beacff50edbd6c9659a6f15fc7f6126909fade29
