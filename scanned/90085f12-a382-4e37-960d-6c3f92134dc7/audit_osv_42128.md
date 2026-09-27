# [H] KVM: x86: Check for invalid/obsolete root *after* making MMU pages available

## Summary
Severity: High
Advisory: CVE-2026-64561
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-64561
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.218, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Check for invalid/obsolete root *after* making MMU pages available

Check for a "stale" page fault, i.e. for an invalid and/or obsolete root,
after making MMU pages available for the shadow MMU.  If reclaiming shadow
pages zaps an in-use root, i.e. marks it invalid, then KVM will attempt to
map memory into an invalid root.  On its own, populating an invalid root is
"fine", but because child shadow pages inherit their parent's role, any
children created during the map/fetch will be created as invalid pages,
thus violating KVM's invariant that invalid pages are never on the list of
active MMU pages.

Note, the underlying flaw has existed since KVM first started tracking
invalid roots in 2008 (commit 2e53d63acba7, "KVM: MMU: ignore zapped root
pagetables"), but the true badness only came along in 2020 (Linux 5.9)
with the invariant that invalid shadow pages can't be on the list of
active pages.

Note #2, inheriting role.invalid when creating child shadow pages is also
far from ideal; that flaw will be addressed separately.

## References
- https://git.kernel.org/stable/c/0026dbb7de8ea76e97d6edf42fc3cc084564e2bf
- https://git.kernel.org/stable/c/2abd5287f08319fa35764566b15c6e22cb1068db
- https://git.kernel.org/stable/c/35e77467610c4a37cb0ff54ee56b85f73b1f5700
- https://git.kernel.org/stable/c/62ef67af1878fa2cd066642f2f59e33ade95f637
- https://git.kernel.org/stable/c/65c4f7a1028cf01a93a2762d679c289810ede990
- https://git.kernel.org/stable/c/bce0d3c26e2c761a4bf43c8949f333fc7374eb2d
- https://git.kernel.org/stable/c/f3477a6a4164f15287444eda685b5f6405dbd1e5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64561.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64561
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/V4bel/Zapscape
