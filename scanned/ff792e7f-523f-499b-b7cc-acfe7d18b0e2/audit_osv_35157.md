# [H] landlock: Fix handling of disconnected directories

## Summary
Severity: High
Advisory: CVE-2025-68736
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68736
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.6.143, >=6.7.0 <6.12.80, >=6.13.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

landlock: Fix handling of disconnected directories

Disconnected files or directories can appear when they are visible and
opened from a bind mount, but have been renamed or moved from the source
of the bind mount in a way that makes them inaccessible from the mount
point (i.e. out of scope).

Previously, access rights tied to files or directories opened through a
disconnected directory were collected by walking the related hierarchy
down to the root of the filesystem, without taking into account the
mount point because it couldn't be found. This could lead to
inconsistent access results, potential access right widening, and
hard-to-debug renames, especially since such paths cannot be printed.

For a sandboxed task to create a disconnected directory, it needs to
have write access (i.e. FS_MAKE_REG, FS_REMOVE_FILE, and FS_REFER) to
the underlying source of the bind mount, and read access to the related
mount point.   Because a sandboxed task cannot acquire more access
rights than those defined by its Landlock domain, this could lead to
inconsistent access rights due to missing permissions that should be
inherited from the mount point hierarchy, while inheriting permissions
from the filesystem hierarchy hidden by this mount point instead.

Landlock now handles files and directories opened from disconnected
directories by taking into account the filesystem hierarchy when the
mount point is not found in the hierarchy walk, and also always taking
into account the mount point from which these disconnected directories
were opened.  This ensures that a rename is not allowed if it would
widen access rights [1].

The rationale is that, even if disconnected hierarchies might not be
visible or accessible to a sandboxed task, relying on the collected
access rights from them improves the guarantee that access rights will
not be widened during a rename because of the access right comparison
between the source and the destination (see LANDLOCK_ACCESS_FS_REFER).
It may look like this would grant more access on disconnected files and
directories, but the security policies are always enforced for all the
evaluated hierarchies.  This new behavior should be less surprising to
users and safer from an access control perspective.

Remove a wrong WARN_ON_ONCE() canary in collect_domain_accesses() and
fix the related comment.

Because opened files have their access rights stored in the related file
security properties, there is no impact for disconnected or unlinked
files.

## References
- https://git.kernel.org/stable/c/426d5b681b2f3339ff04da39b81d71176dc8c87c
- https://git.kernel.org/stable/c/49c9e09d961025b22e61ef9ad56aa1c21b6ce2f1
- https://git.kernel.org/stable/c/cadb28f8b3fd6908e3051e86158c65c3a8e1c907
- https://git.kernel.org/stable/c/fbf718d5afe21057694a0c0223a18b0c7a5960b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68736.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68736
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
