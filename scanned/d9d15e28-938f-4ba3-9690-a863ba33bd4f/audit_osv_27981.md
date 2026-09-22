# [H] inet: inet_defrag: prevent sk release while still in use

## Summary
Severity: High
Advisory: CVE-2024-26921
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-18
Source: https://osv.dev/vulnerability/CVE-2024-26921
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

inet: inet_defrag: prevent sk release while still in use

ip_local_out() and other functions can pass skb->sk as function argument.

If the skb is a fragment and reassembly happens before such function call
returns, the sk must not be released.

This affects skb fragments reassembled via netfilter or similar
modules, e.g. openvswitch or ct_act.c, when run as part of tx pipeline.

Eric Dumazet made an initial analysis of this bug.  Quoting Eric:
  Calling ip_defrag() in output path is also implying skb_orphan(),
  which is buggy because output path relies on sk not disappearing.

  A relevant old patch about the issue was :
  8282f27449bf ("inet: frag: Always orphan skbs inside ip_defrag()")

  [..]

  net/ipv4/ip_output.c depends on skb->sk being set, and probably to an
  inet socket, not an arbitrary one.

  If we orphan the packet in ipvlan, then downstream things like FQ
  packet scheduler will not work properly.

  We need to change ip_defrag() to only use skb_orphan() when really
  needed, ie whenever frag_list is going to be used.

Eric suggested to stash sk in fragment queue and made an initial patch.
However there is a problem with this:

If skb is refragmented again right after, ip_do_fragment() will copy
head->sk to the new fragments, and sets up destructor to sock_wfree.
IOW, we have no choice but to fix up sk_wmem accouting to reflect the
fully reassembled skb, else wmem will underflow.

This change moves the orphan down into the core, to last possible moment.
As ip_defrag_offset is aliased with sk_buff->sk member, we must move the
offset into the FRAG_CB, else skb->sk gets clobbered.

This allows to delay the orphaning long enough to learn if the skb has
to be queued or if the skb is completing the reasm queue.

In the former case, things work as before, skb is orphaned.  This is
safe because skb gets queued/stolen and won't continue past reasm engine.

In the latter case, we will steal the skb->sk reference, reattach it to
the head skb, and fix up wmem accouting when inet_frag inflates truesize.

## References
- https://git.kernel.org/stable/c/18685451fc4e546fc0e718580d32df3c0e5c8272
- https://git.kernel.org/stable/c/1b6de5e6575b56502665c65cf93b0ae6aa0f51ab
- https://git.kernel.org/stable/c/4318608dc28ef184158b4045896740716bea23f0
- https://git.kernel.org/stable/c/7d0567842b78390dd9b60f00f1d8f838d540e325
- https://git.kernel.org/stable/c/9705f447bf9a6cd088300ad2c407b5e1c6591091
- https://git.kernel.org/stable/c/e09cbe017311508c21e0739e97198a8388b98981
- https://git.kernel.org/stable/c/f4877225313d474659ee53150ccc3d553a978727
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26921.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26921
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
