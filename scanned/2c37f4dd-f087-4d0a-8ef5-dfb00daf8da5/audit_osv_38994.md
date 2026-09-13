# [H] xfrm: esp: avoid in-place decrypt on shared skb frags

## Summary
Severity: High
Advisory: CVE-2026-43284
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43284
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.255, >=5.11.0 <5.15.205, >=5.16.0 <6.1.171, >=6.2.0 <6.6.138, >=6.7.0 <6.12.87, >=6.13.0 <6.18.28, >=6.19.0 <7.0.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: esp: avoid in-place decrypt on shared skb frags

MSG_SPLICE_PAGES can attach pages from a pipe directly to an skb. TCP
marks such skbs with SKBFL_SHARED_FRAG after skb_splice_from_iter(),
so later paths that may modify packet data can first make a private
copy. The IPv4/IPv6 datagram append paths did not set this flag when
splicing pages into UDP skbs.

That leaves an ESP-in-UDP packet made from shared pipe pages looking
like an ordinary uncloned nonlinear skb. ESP input then takes the no-COW
fast path for uncloned skbs without a frag_list and decrypts in place
over data that is not owned privately by the skb.

Mark IPv4/IPv6 datagram splice frags with SKBFL_SHARED_FRAG, matching
TCP. Also make ESP input fall back to skb_cow_data() when the flag is
present, so ESP does not decrypt externally backed frags in place.
Private nonlinear skb frags still use the existing fast path.

This intentionally does not change ESP output. In esp_output_head(),
the path that appends the ESP trailer to existing skb tailroom without
calling skb_cow_data() is not reachable for nonlinear skbs:
skb_tailroom() returns zero when skb->data_len is nonzero, while ESP
tailen is positive. Thus ESP output will either use the separate
destination-frag path or fall back to skb_cow_data().

## References
- http://www.openwall.com/lists/oss-security/2026/05/08/7
- http://www.openwall.com/lists/oss-security/2026/05/13/6
- http://www.openwall.com/lists/oss-security/2026/05/14/2
- http://www.openwall.com/lists/oss-security/2026/05/14/4
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/50ed1e7873100f77abad20fd31c51029bc49cd03
- https://git.kernel.org/stable/c/52646cbd00e765a6db9c3afe9535f26218276034
- https://git.kernel.org/stable/c/5d55c7336f8032d434adcc5fab987ccc93a44aec
- https://git.kernel.org/stable/c/71a1d9d985d26716f74d21f18ee8cac821b06e97
- https://git.kernel.org/stable/c/8253aab4659ca16116b522203c2a6b18dccacea7
- https://git.kernel.org/stable/c/a6cb440f274a22456ef3e86b457344f1678f38f9
- https://git.kernel.org/stable/c/ab8b995323e5237041472d07e5055f5f7dcdf15b
- https://git.kernel.org/stable/c/b54edf1e9a3fd3491bdcb82a21f8d21315271e0d
- https://git.kernel.org/stable/c/f4c50a4034e62ab75f1d5cdd191dd5f9c77fdff4
- https://git.kernel.org/stable/c/fe785bb3a8096dffcc4048a85cd0c83337eeecad
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43284.json
- https://www.vicarius.io/vsociety/posts/cve-2026-43284-detection-script-dirty-frag-linux-kernel-local-privilege-escalation
- https://www.vicarius.io/vsociety/posts/cve-2026-43284-mitigation-script-dirty-frag-linux-kernel-local-privilege-escalation
- https://access.redhat.com/errata/RHSA-2026:16061
