# [H] vmxnet3: Fix malformed packet sizing in vmxnet3_process_xdp

## Summary
Severity: High
Advisory: CVE-2025-37799
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2025-05-03
Source: https://osv.dev/vulnerability/CVE-2025-37799
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.89, >=6.7.0 <6.12.26, >=6.9.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

vmxnet3: Fix malformed packet sizing in vmxnet3_process_xdp

vmxnet3 driver's XDP handling is buggy for packet sizes using ring0 (that
is, packet sizes between 128 - 3k bytes).

We noticed MTU-related connectivity issues with Cilium's service load-
balancing in case of vmxnet3 as NIC underneath. A simple curl to a HTTP
backend service where the XDP LB was doing IPIP encap led to overly large
packet sizes but only for *some* of the packets (e.g. HTTP GET request)
while others (e.g. the prior TCP 3WHS) looked completely fine on the wire.

In fact, the pcap recording on the backend node actually revealed that the
node with the XDP LB was leaking uninitialized kernel data onto the wire
for the affected packets, for example, while the packets should have been
152 bytes their actual size was 1482 bytes, so the remainder after 152 bytes
was padded with whatever other data was in that page at the time (e.g. we
saw user/payload data from prior processed packets).

We only noticed this through an MTU issue, e.g. when the XDP LB node and
the backend node both had the same MTU (e.g. 1500) then the curl request
got dropped on the backend node's NIC given the packet was too large even
though the IPIP-encapped packet normally would never even come close to
the MTU limit. Lowering the MTU on the XDP LB (e.g. 1480) allowed to let
the curl request succeed (which also indicates that the kernel ignored the
padding, and thus the issue wasn't very user-visible).

Commit e127ce7699c1 ("vmxnet3: Fix missing reserved tailroom") was too eager
to also switch xdp_prepare_buff() from rcd->len to rbi->len. It really needs
to stick to rcd->len which is the actual packet length from the descriptor.
The latter we also feed into vmxnet3_process_xdp_small(), by the way, and
it indicates the correct length needed to initialize the xdp->{data,data_end}
parts. For e127ce7699c1 ("vmxnet3: Fix missing reserved tailroom") the
relevant part was adapting xdp_init_buff() to address the warning given the
xdp_data_hard_end() depends on xdp->frame_sz. With that fixed, traffic on
the wire looks good again.

## References
- https://git.kernel.org/stable/c/33e131a10459d16f181c8184d3f17f1c318c7002
- https://git.kernel.org/stable/c/4c2227656d9003f4d77afc76f34dd81b95e4c2c4
- https://git.kernel.org/stable/c/c4312c4d244aa58e811ff0297e013124d115e793
- https://git.kernel.org/stable/c/e3ad76e36a37b0ff4a71b06d5b33530ee8c3a177
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37799.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37799
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
