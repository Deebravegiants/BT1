# [C] ipv6: ioam: refresh hdr pointer before ioam6_event()

## Summary
Severity: Critical
Advisory: CVE-2026-64132
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64132
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: ioam: refresh hdr pointer before ioam6_event()

Reported by Sashiko:

In ipv6_hop_ioam(), the hdr pointer is initialized to point into the
skb's linear data buffer. Later, the code calls skb_ensure_writable(),
which might reallocate the buffer:

	if (skb_ensure_writable(skb, optoff + 2 + hdr->opt_len))
		goto drop;

	/* Trace pointer may have changed */
	trace = (struct ioam6_trace_hdr *)(skb_network_header(skb)
					   + optoff + sizeof(*hdr));

	ioam6_fill_trace_data(skb, ns, trace, true);

	ioam6_event(IOAM6_EVENT_TRACE, dev_net(skb->dev),
		    GFP_ATOMIC, (void *)trace, hdr->opt_len - 2);

If the skb is cloned or lacks sufficient linear headroom,
skb_ensure_writable() will invoke pskb_expand_head(), which reallocates
the skb's data buffer and frees the old one, invalidating pointers to
it. While the code recalculates the trace pointer immediately after the
call to skb_ensure_writable(), it fails to recalculate the hdr pointer.

This patch fixes the above by recalculating the hdr pointer before
passing hdr->opt_len to ioam6_event(), so that we avoid any UaF.

## References
- https://git.kernel.org/stable/c/24de676da63c1122d2c13b0d546238b66d1b4e62
- https://git.kernel.org/stable/c/5af905aa8e91ff8d94572a1e089558f21dcf24ed
- https://git.kernel.org/stable/c/769723124b7c3b2bfea4cf68ad292698b87c8d01
- https://git.kernel.org/stable/c/e46e6bc97fb1f339730ff1ba74267fbf48e7a422
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64132.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64132
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
