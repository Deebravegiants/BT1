# [C] um: vector: fix use-after-free in vector_mmsg_rx()

## Summary
Severity: Critical
Advisory: CVE-2026-74478
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74478
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

um: vector: fix use-after-free in vector_mmsg_rx()

When vector_mmsg_rx() discards a packet whose overlay header fails
verify_header(), it frees the skb and continues the loop:

	if (header_check < 0) {
		dev_kfree_skb_irq(skb);
		vp->estats.rx_encaps_errors++;
		continue;
	}

The normal and short-packet paths fall through to the bottom of the
loop body, which clears the consumed slot and advances the cursors:

	(*skbuff_vector) = NULL;
	mmsg_vector++;
	skbuff_vector++;

The verify_header() < 0 path skips that via continue, so the freed skb
is left in skbuff_vector[] and the cursors do not advance. The next
iteration reads the same slot, gets the freed skb, and frees it again,
producing a refcount underflow / use-after-free in the RX path.

Discard the slot the same way the other paths do before continuing.

Only transports whose verify_header() can return negative are affected:
GRE and L2TPv3 do so on a cookie/session-id mismatch (raw/tap do not),
so any peer on such a transport can trigger it without authentication.

## References
- https://git.kernel.org/stable/c/180ff4c81faf01ec4e06082c9daa7c40518ead89
- https://git.kernel.org/stable/c/4b9601595e8b6b5d18878cac0aeabc687d241111
- https://git.kernel.org/stable/c/67d58ab4f2ccf7145f3da07e025735a09c79de1b
- https://git.kernel.org/stable/c/7dc9781e320d664c9bdd50003c9acfddf363d1e1
- https://git.kernel.org/stable/c/804b681002ead233abf49a3efd681f5468a835f9
- https://git.kernel.org/stable/c/967c779c9853d2a1cc9cd8e61d300250c348f3d9
- https://git.kernel.org/stable/c/a7bc015bb798c525e7a82dd14225c6aeb994274b
- https://git.kernel.org/stable/c/af421e9aed3920c7ac88c24daa48606c7112feca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74478.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74478
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
