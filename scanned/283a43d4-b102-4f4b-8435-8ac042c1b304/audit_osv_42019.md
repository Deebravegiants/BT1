# [C] bpf: Reject fragmented frames in devmap

## Summary
Severity: Critical
Advisory: CVE-2026-64355
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64355
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reject fragmented frames in devmap

Devmap broadcast redirects clone the packet for all but the last
destination.

For native XDP, that clone path copies only the linear xdp_frame data,
while fragmented frames keep skb_shared_info in tailroom outside the
linear area. Cloning such a frame leaves XDP_FLAGS_HAS_FRAGS set but
without valid frag metadata, and the later free path can interpret
uninitialized tail data as skb_shared_info, leading to an out-of-bounds
access during frame return.

Reject fragmented native XDP frames in dev_map_enqueue_clone().

Add the same restriction to the generic XDP clone path in
dev_map_redirect_clone(). Generic XDP represents fragmented packets as
nonlinear skbs, and rejecting them here keeps clone-based broadcast
support aligned between native and generic XDP.

## References
- https://git.kernel.org/stable/c/07a4c11ee8ef4abcb39d922e9e410ae269671cdf
- https://git.kernel.org/stable/c/47baddc856ae7e93a565dd9deeb797999b179466
- https://git.kernel.org/stable/c/51d07c12ca411e692c424ecdabf077f1e61a61be
- https://git.kernel.org/stable/c/a9bb2d9c798cb62a4050a991c27b752770c33afe
- https://git.kernel.org/stable/c/aa496720618f1a6054f1c870bf10b4f6c99bf656
- https://git.kernel.org/stable/c/bccbab36ff228e0825eb85d9b0f9b8434cd0a399
- https://git.kernel.org/stable/c/c5b4f5efcb55c1af3fe44ff712d31b7fb098a831
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64355.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64355
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
