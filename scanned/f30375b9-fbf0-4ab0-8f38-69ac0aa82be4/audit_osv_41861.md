# [C] netfilter: synproxy: refresh tcphdr after skb_ensure_writable

## Summary
Severity: Critical
Advisory: CVE-2026-64007
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64007
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: synproxy: refresh tcphdr after skb_ensure_writable

synproxy_tstamp_adjust() rewrites the TCP timestamp option in place
and then patches the TCP checksum via inet_proto_csum_replace4() on
the caller-supplied tcphdr pointer.  Both ipv4_synproxy_hook() and
ipv6_synproxy_hook() obtain that pointer with skb_header_pointer()
before calling in, so it may either alias skb->head directly or
point at the caller's on-stack _tcph buffer.

Between obtaining the pointer and using it, the function calls
skb_ensure_writable(skb, optend), which on a cloned or non-linear
skb invokes pskb_expand_head() and frees the old skb->head.  After
that point the cached th is stale:

    caller (ipv[46]_synproxy_hook)
      th = skb_header_pointer(skb, ..., &_tcph)
      synproxy_tstamp_adjust(skb, protoff, th, ...)
        skb_ensure_writable(skb, optend)
          pskb_expand_head()        /* kfree(old skb->head) */
        ...
        inet_proto_csum_replace4(&th->check, ...)
                                    /* writes into freed head, or
                                       into the caller's stack copy
                                       leaving the on-wire checksum
                                       stale */

The option bytes are written through skb->data and are fine; only
the checksum update goes through th and so lands in the wrong
place.  The result is either a write into freed slab memory or a
packet leaving with a checksum that does not match its payload.

Fix by re-deriving th from skb->data + protoff immediately after
skb_ensure_writable() succeeds, so the subsequent checksum update
targets the linear, writable header.

## References
- https://git.kernel.org/stable/c/92170e6afe927ab2792a3f71902845789c8e31b1
- https://git.kernel.org/stable/c/9902a1058992de5d95656b64a3bd95c077f7ba2c
- https://git.kernel.org/stable/c/a91887a5b6ee4b98dfbf1db657ed2b879430149e
- https://git.kernel.org/stable/c/af2c22ccb1f621aff487ff47a040e38e058541e7
- https://git.kernel.org/stable/c/c7f945f7da097245a2f8ed7775ce48421047ee96
- https://git.kernel.org/stable/c/d3019c61799adc21811af4b521f11f3dc77f8e04
- https://git.kernel.org/stable/c/dd206819f210522579010d889d45a9530bb494bc
- https://git.kernel.org/stable/c/f0fea2b6d5453a11ad11713bbf37561b9b3a7edf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64007.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64007
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
