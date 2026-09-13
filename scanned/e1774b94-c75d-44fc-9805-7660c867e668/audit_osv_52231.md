# [M] CVE-2021-47223

## Summary
Severity: Medium
Advisory: CVE-2021-47223
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47223
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bridge: fix vlan tunnel dst null pointer dereference

This patch fixes a tunnel_dst null pointer dereference due to lockless
access in the tunnel egress path. When deleting a vlan tunnel the
tunnel_dst pointer is set to NULL without waiting a grace period (i.e.
while it's still usable) and packets egressing are dereferencing it
without checking. Use READ/WRITE_ONCE to annotate the lockless use of
tunnel_id, use RCU for accessing tunnel_dst and make sure it is read
only once and checked in the egress path. The dst is already properly RCU
protected so we don't need to do anything fancy than to make sure
tunnel_id and tunnel_dst are read only once and checked in the egress path.

## References
- https://git.kernel.org/stable/c/24a6e55f17aa123bc1fc54b7d3c410b41bc16530
- https://git.kernel.org/stable/c/58e2071742e38f29f051b709a5cca014ba51166f
- https://git.kernel.org/stable/c/a2241e62f6b4a774d8a92048fdf59c45f6c2fe5c
- https://git.kernel.org/stable/c/abb02e05cb1c0a30dd873a29f33bc092067dc35d
- https://git.kernel.org/stable/c/ad7feefe7164892db424c45687472db803d87f79
- https://git.kernel.org/stable/c/fe0448a3fad365a747283a00a1d1ad5e8d6675b7
