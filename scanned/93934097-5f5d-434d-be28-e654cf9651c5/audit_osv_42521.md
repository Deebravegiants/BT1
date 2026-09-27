# [H] firewire: net: Fix fragmented datagram reassembly

## Summary
Severity: High
Advisory: CVE-2026-68354
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68354
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

firewire: net: Fix fragmented datagram reassembly

fwnet_frag_new() keeps a sorted list of received fragments for a partial
datagram. When a new fragment is adjacent to an existing fragment, the
code checks whether the new fragment also closes the gap to the next or
previous list entry.

Those neighbor lookups currently assume that the current fragment always
has a real next or previous fragment. At a list edge, the next or
previous entry is the list head, not a struct fwnet_fragment_info.

The gap checks also compare against the old edge of the current fragment
instead of the edge after adding the new fragment. As a result, a
fragment that bridges two existing ranges may leave two adjacent ranges
unmerged, so fwnet_pd_is_complete() can miss a complete datagram.

Check for the list head before looking up the neighboring fragment, and
compare the neighbor against the new fragment's far edge when deciding
whether to merge all three ranges.

This issue was found by a static analysis checker and confirmed by
manual source review.

## References
- https://git.kernel.org/stable/c/0177e578d7a885037b0fb82286c12e9d0360cc10
- https://git.kernel.org/stable/c/0a219b2a01b4fe93706717e3bcacf7f62967b26f
- https://git.kernel.org/stable/c/1aaf16031d65ccd4576451a79f7dabbec994c111
- https://git.kernel.org/stable/c/22e05b8ddbcf7d22c7f1598786e86635547e554d
- https://git.kernel.org/stable/c/268cea3800eda5fa3ee04a49ee2973b8766a8df3
- https://git.kernel.org/stable/c/2a5aa4e9b89227d1a1690fb8d5b81e5f3b261999
- https://git.kernel.org/stable/c/b7d633c7c92321be98724b1d365e8ce507f2f349
- https://git.kernel.org/stable/c/d52a13adbb8ccbab99cd3bad36804e87d8b5c052
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68354.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68354
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
