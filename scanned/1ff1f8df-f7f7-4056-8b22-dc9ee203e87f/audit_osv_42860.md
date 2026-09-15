# [H] fhandle: reject detached mounts in capable_wrt_mount()

## Summary
Severity: High
Advisory: CVE-2026-72034
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72034
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fhandle: reject detached mounts in capable_wrt_mount()

The recent fhandle RCU fix moved the mount namespace capability check
into capable_wrt_mount(), so a non-NULL mnt_namespace survives the
ns_capable() dereference. The helper still assumes the later
READ_ONCE(mount->mnt_ns) must be non-NULL because may_decode_fh()
checked is_mounted() first.

That assumption is not stable. A detached mount from
open_tree(..., OPEN_TREE_CLONE) can be dissolved on fput while
open_by_handle_at() is between those checks, and umount_tree() can
clear mount->mnt_ns. If the helper observes NULL, it dereferences
mnt_ns->user_ns and panics.

Return false when the RCU read observes a detached mount. This keeps
the relaxed permission path conservative: a mount no longer attached
to a namespace cannot authorize open_by_handle_at() access.

## References
- https://git.kernel.org/stable/c/15104234c267ebe04b9f9a73e5c2179cc265ff60
- https://git.kernel.org/stable/c/6c52226072a3c61337b1eec1799bb987748884fa
- https://git.kernel.org/stable/c/6c732471740bc2ac9b0946134f9f551dc75f4369
- https://git.kernel.org/stable/c/6ee183d89261bf1d1cf9f06d80a40dab8f36ee55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72034.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72034
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
