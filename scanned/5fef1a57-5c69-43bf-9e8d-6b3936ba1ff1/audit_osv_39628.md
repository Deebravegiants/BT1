# [H] net: gro: don't merge zcopy skbs

## Summary
Severity: High
Advisory: CVE-2026-46323
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46323
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.176, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: gro: don't merge zcopy skbs

skb_gro_receive() can currently copy frags between the source and GRO
skb, without checking the zerocopy status, and in particular the
SKBFL_MANAGED_FRAG_REFS flag.

When SKBFL_MANAGED_FRAG_REFS is set, the skb doesn't hold a reference
on the pages in shinfo->frags. Appending those frags to another skb's
frags without fixing up the page refcount can lead to UAF.

When either the last skb in the GRO chain (the one we would append
frags to) or the source skb is zerocopy, don't merge the skbs.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1f9c828556416fbe3f49386708ce999fc4d4da06
- https://git.kernel.org/stable/c/3c6cc9f2ca65b6dd61b1af75452dc0e1cd0aad8d
- https://git.kernel.org/stable/c/44bea2032af0425e4ce6d26a8af0ede79db49ec1
- https://git.kernel.org/stable/c/479084ae0e1d9cb7929cb4298d35623de189f80a
- https://git.kernel.org/stable/c/4db79a322db8c97f7b73b8a347395ef4d685eb40
- https://git.kernel.org/stable/c/e334cbf3388fd9334503a778a82d9e9f14dd2f71
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46323.json
- https://access.redhat.com/errata/RHSA-2026:27708
- https://access.redhat.com/errata/RHSA-2026:27731
- https://access.redhat.com/errata/RHSA-2026:27735
- https://access.redhat.com/errata/RHSA-2026:36018
- https://access.redhat.com/errata/RHSA-2026:44230
- https://access.redhat.com/errata/RHSA-2026:44231
- https://access.redhat.com/errata/RHSA-2026:44259
- https://access.redhat.com/errata/RHSA-2026:44262
- https://access.redhat.com/errata/RHSA-2026:44270
- https://access.redhat.com/errata/RHSA-2026:47727
- https://access.redhat.com/errata/RHSA-2026:62639
- https://access.redhat.com/errata/RHSA-2026:62640
