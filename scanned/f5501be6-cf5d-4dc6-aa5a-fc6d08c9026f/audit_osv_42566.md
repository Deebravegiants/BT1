# [H] btrfs: don't propagate EXTENT_FLAG_LOGGING to split extent maps

## Summary
Severity: High
Advisory: CVE-2026-68442
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68442
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: don't propagate EXTENT_FLAG_LOGGING to split extent maps

When btrfs_drop_extent_map_range() splits an extent map, the new split
maps inherit the original map's flags through a local 'flags' variable.
Commit f86f7a75e2fb ("btrfs: use the flags of an extent map to identify
the compression type") changed the EXTENT_FLAG_LOGGING clearing to
operate on em->flags instead of that local 'flags' copy, so a split of
an extent map that is currently being logged wrongly inherits
EXTENT_FLAG_LOGGING.

The flag is then never cleared on the split, and when it is freed while
still on the inode's modified_extents list (for example by the extent
map shrinker) it trips the WARN_ON(!list_empty(&em->list)) in
btrfs_free_extent_map() and leads to a use-after-free.

Clear EXTENT_FLAG_LOGGING from the local 'flags' copy used for the
splits and only clear EXTENT_FLAG_PINNED from em->flags, restoring the
behaviour prior to f86f7a75e2fb.

## References
- https://git.kernel.org/stable/c/0e465c63f103a5ce6849614d6bda048d70eebec8
- https://git.kernel.org/stable/c/2a9246a424f45f33a1b8367052611ebe874868ad
- https://git.kernel.org/stable/c/5eff4d5b17fa1950e80bfd1ba43dc0699e61a644
- https://git.kernel.org/stable/c/9304713b70e7e1450e3a76e758836fe5391bfa95
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68442.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68442
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
