# [H] net: skbuff: propagate shared-frag marker through frag-transfer helpers

## Summary
Severity: High
Advisory: CVE-2026-43503
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-23
Source: https://osv.dev/vulnerability/CVE-2026-43503
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.257, >=5.11.0 <5.15.208, >=5.16.0 <6.1.174, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: skbuff: propagate shared-frag marker through frag-transfer helpers

Two frag-transfer helpers (__pskb_copy_fclone() and skb_shift()) fail
to propagate the SKBFL_SHARED_FRAG bit in skb_shinfo()->flags when
moving frags from source to destination.  __pskb_copy_fclone() defers
the rest of the shinfo metadata to skb_copy_header() after copying
frag descriptors, but that helper only carries over gso_{size,segs,
type} and never touches skb_shinfo()->flags; skb_shift() moves frag
descriptors directly and leaves flags untouched.  As a result, the
destination skb keeps a reference to the same externally-owned or
page-cache-backed pages while reporting skb_has_shared_frag() as
false.

The mismatch is harmful in any in-place writer that uses
skb_has_shared_frag() to decide whether shared pages must be detoured
through skb_cow_data().  ESP input is one such writer (esp4.c,
esp6.c), and a single nft 'dup to <local>' rule -- or any other
nf_dup_ipv4() / xt_TEE caller -- is enough to land a pskb_copy()'d
skb in esp_input() with the marker stripped, letting an unprivileged
user write into the page cache of a root-owned read-only file via
authencesn-ESN stray writes.

Set SKBFL_SHARED_FRAG on the destination whenever frag descriptors
were actually moved from the source.  skb_copy() and skb_copy_expand()
share skb_copy_header() too but linearize all paged data into freshly
allocated head storage and emerge with nr_frags == 0, so
skb_has_shared_frag() returns false on its own; they need no change.

The same omission exists in skb_gro_receive() and skb_gro_receive_list().
The former moves the incoming skb's frag descriptors into the
accumulator's last sub-skb via two paths (a direct frag-move loop and
the head_frag + memcpy path); the latter chains the incoming skb whole
onto p's frag_list.  Downstream skb_segment() reads only
skb_shinfo(p)->flags, and skb_segment_list() reuses each sub-skb's
shinfo as the nskb -- both p and lp must carry the marker.

The same omission also exists in tcp_clone_payload(), which builds an
MTU probe skb by moving frag descriptors from skbs on sk_write_queue
into a freshly allocated nskb.  The helper falls into the same family
and warrants the same fix for consistency; no TCP TX-side in-place
writer is currently known to reach a user page through this gap, but
a future consumer depending on the marker would regress silently.

The same omission exists in skb_segment(): the per-iteration flag
merge takes only head_skb's flag, and the inner switch that rebinds
frag_skb to list_skb on head_skb-frags exhaustion does not fold the
new frag_skb's flag into nskb.  Fold frag_skb's flag at both sites
so segments drawing frags from frag_list members carry the marker.

## References
- https://git.kernel.org/stable/c/12401fcfb01f53ccc63ab0a3246570fe8f3105ee
- https://git.kernel.org/stable/c/179f1852bdedc300e373e807cc102cd81feff196
- https://git.kernel.org/stable/c/48f6a5356a33dd78e7144ae1faef95ffc990aae0
- https://git.kernel.org/stable/c/989214c66884d70716d83dc1d0bf5e16287bf349
- https://git.kernel.org/stable/c/9bc9d6d6967a2239aa57af2aa53554eddd640d20
- https://git.kernel.org/stable/c/fbeab9555564a1b98e8582cd106dfe46c4606991
- https://git.kernel.org/stable/c/fc6eb39c55e97df2f94ad974b8a5bbcd019da2c8
- https://git.kernel.org/stable/c/ff375cc75f9167168db38e0464a482d5fbc8d81d
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43503.json
- https://access.redhat.com/errata/RHSA-2026:19521
- https://access.redhat.com/errata/RHSA-2026:19540
- https://access.redhat.com/errata/RHSA-2026:19568
- https://access.redhat.com/errata/RHSA-2026:19569
- https://access.redhat.com/errata/RHSA-2026:19664
- https://access.redhat.com/errata/RHSA-2026:19666
- https://access.redhat.com/errata/RHSA-2026:19705
- https://access.redhat.com/errata/RHSA-2026:19711
- https://access.redhat.com/errata/RHSA-2026:19875
- https://access.redhat.com/errata/RHSA-2026:20051
- https://access.redhat.com/errata/RHSA-2026:20054
