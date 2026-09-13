# [H] wifi: mac80211: consume only present negotiated TTLM maps

## Summary
Severity: High
Advisory: CVE-2026-64223
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64223
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: consume only present negotiated TTLM maps

ieee80211_tid_to_link_map_size_ok() validates negotiated TTLM elements
against the number of link-map entries indicated by link_map_presence.
ieee80211_parse_neg_ttlm() must consume the same layout.

The parser advanced its cursor for every TID, including TIDs whose
presence bit is clear and therefore have no map bytes in the element.
A sparse map can then make a later present TID read past the validated
element.

The bad bytes land in neg_ttlm->{up,down}link[tid] but are gated by
valid_links before being applied to driver state, so a peer cannot
turn the read into a policy change.  Under KUnit + KASAN with an
exact-sized element allocation the OOB read is reported as a
slab-out-of-bounds; whether the same trigger fires under the
production RX path depends on surrounding allocator state.

Advance the cursor only when the current TID has a map present.

## References
- https://git.kernel.org/stable/c/2becaaeebe230ade1fcd5d0f1cde4d6ee93ec78f
- https://git.kernel.org/stable/c/2dd9304727c7041df0a599595910bdbe02ad03c5
- https://git.kernel.org/stable/c/a6e6ccd5bd07155c2add6c74ce1a5e68ad3b95ea
- https://git.kernel.org/stable/c/f7d395dc5008168ac5b9c1ac2791e59a6078cca1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64223.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64223
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
