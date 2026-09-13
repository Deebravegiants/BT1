# [H] ipv4: raw: reject IP_HDRINCL packets with ihl < 5

## Summary
Severity: High
Advisory: CVE-2026-64114
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64114
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: raw: reject IP_HDRINCL packets with ihl < 5

raw_send_hdrinc() validates that the caller-supplied IPv4 header
fits within the message length:

    iphlen = iph->ihl * 4;
    err = -EINVAL;
    if (iphlen > length)
        goto error_free;

    if (iphlen >= sizeof(*iph)) {
        /* fix up saddr, tot_len, id, csum, transport_header */
    }

It does not, however, reject ihl < 5.  For such a packet the
"if (iphlen >= sizeof(*iph))" branch is skipped, leaving the
crafted iphdr untouched, but the packet is still handed to
__ip_local_out() and onward.  Downstream consumers that read
iph->ihl assume a sane value: net/ipv4/ah4.c:ah_output() in
particular subtracts sizeof(struct iphdr) from top_iph->ihl * 4
and passes the (signed-int-negative, then cast to size_t)
result to memcpy(), producing an OOB access of length close to
SIZE_MAX and a host kernel panic.

An IPv4 header with ihl < 5 is malformed by definition (RFC 791:
"Internet Header Length is the length of the internet header in
32 bit words ... Note that the minimum value for a correct header
is 5.").  The kernel should not be willing to inject such a
packet into its own output path.

Reject "iphlen < sizeof(*iph)" alongside the existing
"iphlen > length" check.  This matches the principle that locally
constructed packets that re-enter the IP stack must pass the same
basic sanity tests that a foreign packet would be subjected to.

Once this lands, the "if (iphlen >= sizeof(*iph))" wrapper around
the fixup branch becomes redundant; left in place to keep the
patch minimal and backport-friendly.  A follow-up can unwrap it.

Note that commit 86f4c90a1c5c ("ipv4, ipv6: ensure raw socket
message is big enough to hold an IP header") ensures the message
buffer is large enough to hold an iphdr, but does not constrain
the self-reported iph->ihl.

Reachability: the malformed packet source is any caller with
CAP_NET_RAW, including an unprivileged process in a user+net
namespace on a kernel with CONFIG_USER_NS=y.  The reproduced AH
crash also requires a matching xfrm AH policy on the outgoing
route; a container granted CAP_NET_ADMIN can install that state
and policy in its netns.  Loopback bypasses xfrm_output, so the
trigger uses a real netdev.

Reproduced on UML + KASAN: kernel-mode fault at addr 0x0 with
memcpy_orig at the crash site.  Same shape reproduces inside a
rootless Docker container with --cap-add NET_ADMIN on a stock
distro kernel.

## References
- https://git.kernel.org/stable/c/1065b9efa4126df559b03a849c139ecfae92cd25
- https://git.kernel.org/stable/c/145e9afa5b905229b4788bb72c3255f5a5f77508
- https://git.kernel.org/stable/c/3c5411fa4944ed99af3d9d1de750ea8169b6dac9
- https://git.kernel.org/stable/c/5a564f737ec54d63e8ee221d3ff396d07586d464
- https://git.kernel.org/stable/c/7725cd3b471740fd23d25ed1da722c671fb2a5d3
- https://git.kernel.org/stable/c/915fab69823a14c170dbaa3b41978768e0fe62fc
- https://git.kernel.org/stable/c/bbe0be67de296176e7243c76e3d9f02f6ae9ff0b
- https://git.kernel.org/stable/c/bc20dbd48c26e743f7e0845020c11ed2ce8b15ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64114.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64114
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
