# [H] vxlan: mdb: Fix source list corruption on a failed replace

## Summary
Severity: High
Advisory: CVE-2026-68116
Ecosystem: Linux
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68116
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: mdb: Fix source list corruption on a failed replace

When replacing the source list of an MDB remote entry, all existing
sources are first marked for deletion and vxlan_mdb_remote_srcs_add()
is then called to add the new source list. Sources present in the new
list have their deletion mark cleared, and any sources left marked
afterwards are removed.

If vxlan_mdb_remote_srcs_add() fails partway through, its error path
deletes all entries on the remote's source list. That rollback is only
correct for its other caller, vxlan_mdb_remote_add(), where the remote
was just allocated and the list contains solely entries added during
the call. On the replace path the list also holds pre-existing sources,
so a failed replace tears them down together with their (S, G)
forwarding entries instead of leaving the entry unchanged.

This is reachable from an existing (*, G) remote. An EXCLUDE filter
that loses sources starts forwarding traffic that should be blocked,
while an INCLUDE filter that loses sources drops traffic that should be
forwarded.

Mark entries created during the current pass with a new
VXLAN_SGRP_F_NEW flag. On failure, delete only those entries and clear
the deletion mark on the pre-existing ones, so a failed replace leaves
the source list untouched. Retain the flag until the whole operation
succeeds and then clear it. Also stop vxlan_mdb_remote_src_add() from
deleting a pre-existing entry it only looked up when adding that
entry's forwarding entry fails.

## References
- https://git.kernel.org/stable/c/2c54dff57606590fa4abec46bab6bea3133f1539
- https://git.kernel.org/stable/c/54a3c27b357dfb34f327f89bfadeb998bef8051e
- https://git.kernel.org/stable/c/5bc8fc1d2ff802eec839e03adef5df597421898d
- https://git.kernel.org/stable/c/79370b573e92e8f190eb5f9a511fa5398340d8b2
- https://git.kernel.org/stable/c/dcd9b465965422b9654f6026e8a2fa8984f74c3c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68116.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
