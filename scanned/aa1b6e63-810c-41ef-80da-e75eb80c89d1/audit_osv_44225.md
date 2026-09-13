# [H] net: dst_metadata: fix false-positive memcpy overflow in tun_dst_unclone

## Summary
Severity: High
Advisory: CVE-2026-80615
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80615
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dst_metadata: fix false-positive memcpy overflow in tun_dst_unclone

kmalloc_flex() in metadata_dst_alloc() sets __counted_by for the
structure to the options_len, which is then initialized to zero.
Later, we're initializing the structure by copying the tunnel info
together with the options, and this triggers a warning for a potential
memcpy overflow, since the compiler estimates that the options can't
fit into the structure, even though the memory for them is actually
allocated.

 memcpy: detected buffer overflow: 104 byte write of buffer size 96
 WARNING: CPU: X PID: Y at lib/string_helpers.c:1036 __fortify_report
  skb_tunnel_info_unclone+0x179/0x190
  geneve_xmit+0x7fe/0xe00

The issue is triggered when built with clang and source fortification.

Fix that by doing the copy in two stages: first - the main data with
the options_len, then the options.  This way the correct length should
be known at the time of the copy.

It would be better if the options_len never changed after allocation,
but the allocation code is a little separate from the initialization
and it would be awkward and potentially dangerous to return a struct
with options_len set to a non-zero value from the metadata_dst_alloc().

Another option would be to use ip_tunnel_info_opts_set(), but it is
doing too many unnecessary operations for the use case here.

## References
- https://git.kernel.org/stable/c/4c6d43db2a4d2cef3921e885cf34798f790d34ea
- https://git.kernel.org/stable/c/7ce31739fe88a558370135db95bbeec1e7ddfc29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80615.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80615
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
