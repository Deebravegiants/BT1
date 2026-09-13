# [C] ipv6: ioam: fix heap buffer overflow in __ioam6_fill_trace_data()

## Summary
Severity: Critical
Advisory: CVE-2026-43186
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43186
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: ioam: fix heap buffer overflow in __ioam6_fill_trace_data()

On the receive path, __ioam6_fill_trace_data() uses trace->nodelen
to decide how much data to write for each node. It trusts this field
as-is from the incoming packet, with no consistency check against
trace->type (the 24-bit field that tells which data items are
present). A crafted packet can set nodelen=0 while setting type bits
0-21, causing the function to write ~100 bytes past the allocated
region (into skb_shared_info), which corrupts adjacent heap memory
and leads to a kernel panic.

Add a shared helper ioam6_trace_compute_nodelen() in ioam6.c to
derive the expected nodelen from the type field, and use it:

  - in ioam6_iptunnel.c (send path, existing validation) to replace
    the open-coded computation;
  - in exthdrs.c (receive path, ipv6_hop_ioam) to drop packets whose
    nodelen is inconsistent with the type field, before any data is
    written.

Per RFC 9197, bits 12-21 are each short (4-octet) fields, so they
are included in IOAM6_MASK_SHORT_FIELDS (changed from 0xff100000 to
0xff1ffc00).

## References
- https://git.kernel.org/stable/c/0591d6509c2ff13f09ea2998434aba0c0472e978
- https://git.kernel.org/stable/c/632d233cf2e64a46865ae2c064ae3c9df7c8864f
- https://git.kernel.org/stable/c/6db8b56eed62baacaf37486e83378a72635c04cc
- https://git.kernel.org/stable/c/e90346a2f1e8917d5760a44a1f61c44e3b36d96b
- https://git.kernel.org/stable/c/ea3632aefc04205436868541638e26f4a74d5637
- https://git.kernel.org/stable/c/f4d9d4b8fd839719d564651671e24c62c545c23b
- https://git.kernel.org/stable/c/fb3c662fafebc5b9d74417ed1de8759f6bb72143
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43186.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
