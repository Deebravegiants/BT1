# [H] fs/fhandle.c: fix a race in call of has_locked_children()

## Summary
Severity: High
Advisory: CVE-2025-38306
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38306
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.46, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/fhandle.c: fix a race in call of has_locked_children()

may_decode_fh() is calling has_locked_children() while holding no locks.
That's an oopsable race...

The rest of the callers are safe since they are holding namespace_sem and
are guaranteed a positive refcount on the mount in question.

Rename the current has_locked_children() to __has_locked_children(), make
it static and switch the fs/namespace.c users to it.

Make has_locked_children() a wrapper for __has_locked_children(), calling
the latter under read_seqlock_excl(&mount_lock).

## References
- https://git.kernel.org/stable/c/1f282cdc1d219c4a557f7009e81bc792820d9d9a
- https://git.kernel.org/stable/c/287c7d34eedd37af1272dfb3b6e8656f4f026424
- https://git.kernel.org/stable/c/6482c3dccbfb8d20e2856ce67c75856859930b3f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38306.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38306
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
