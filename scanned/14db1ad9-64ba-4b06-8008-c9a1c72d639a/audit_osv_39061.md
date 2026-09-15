# [H] rxrpc: Also unshare DATA/RESPONSE packets when paged frags are present

## Summary
Severity: High
Advisory: CVE-2026-43500
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43500
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.29, >=6.19.0 <7.0.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Also unshare DATA/RESPONSE packets when paged frags are present

The DATA-packet handler in rxrpc_input_call_event() and the RESPONSE
handler in rxrpc_verify_response() copy the skb to a linear one before
calling into the security ops only when skb_cloned() is true.  An skb
that is not cloned but still carries externally-owned paged fragments
(e.g. SKBFL_SHARED_FRAG set by splice() into a UDP socket via
__ip_append_data, or a chained skb_has_frag_list()) falls through to
the in-place decryption path, which binds the frag pages directly into
the AEAD/skcipher SGL via skb_to_sgvec().

Extend the gate to also unshare when skb_has_frag_list() or
skb_has_shared_frag() is true.  This catches the splice-loopback vector
and other externally-shared frag sources while preserving the
zero-copy fast path for skbs whose frags are kernel-private (e.g. NIC
page_pool RX, GRO).  The OOM/trace handling already in place is reused.

## References
- https://git.kernel.org/stable/c/3711382a77342a9a1c3d2e7330dcfc7ea927f568
- https://git.kernel.org/stable/c/3eae0f4f9f7206a4801efa5e0235c25bbd5a412c
- https://git.kernel.org/stable/c/7c504ffab3efce8f7e4f463b314ae31030bdf18b
- https://git.kernel.org/stable/c/aa54b1d27fe0c2b78e664a34fd0fdf7cd1960d71
- https://git.kernel.org/stable/c/d45179f8795222ce858770dc619abe51f9d24411
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43500.json
- https://access.redhat.com/security/cve/CVE-2026-43500
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43500.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43500
- https://bugzilla.redhat.com/show_bug.cgi?id=2468273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/V4bel/dirtyfrag
