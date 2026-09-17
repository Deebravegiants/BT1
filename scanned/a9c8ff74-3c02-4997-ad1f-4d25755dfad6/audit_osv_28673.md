# [H] of: dynamic: Synchronize of_changeset_destroy() with the devlink removals

## Summary
Severity: High
Advisory: CVE-2024-35879
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35879
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.215, >=5.11.0 <5.15.154, >=5.13.0 <6.1.85, >=5.16.0 <6.6.26, >=6.2.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

of: dynamic: Synchronize of_changeset_destroy() with the devlink removals

In the following sequence:
  1) of_platform_depopulate()
  2) of_overlay_remove()

During the step 1, devices are destroyed and devlinks are removed.
During the step 2, OF nodes are destroyed but
__of_changeset_entry_destroy() can raise warnings related to missing
of_node_put():
  ERROR: memory leak, expected refcount 1 instead of 2 ...

Indeed, during the devlink removals performed at step 1, the removal
itself releasing the device (and the attached of_node) is done by a job
queued in a workqueue and so, it is done asynchronously with respect to
function calls.
When the warning is present, of_node_put() will be called but wrongly
too late from the workqueue job.

In order to be sure that any ongoing devlink removals are done before
the of_node destruction, synchronize the of_changeset_destroy() with the
devlink removals.

## References
- https://git.kernel.org/stable/c/3127b2ee50c424a96eb3559fbb7b43cf0b111c7a
- https://git.kernel.org/stable/c/3ee2424107546d882e1ddd75333ca9c32879908c
- https://git.kernel.org/stable/c/7b6df050c45a1ea158fd50bc32a8e1447dd1e951
- https://git.kernel.org/stable/c/801c8b8ec5bfb3519566dff16a5ecd48302fca82
- https://git.kernel.org/stable/c/8917e7385346bd6584890ed362985c219fe6ae84
- https://git.kernel.org/stable/c/ae6d76e4f06c37a623e357e79d49b17411db6f5c
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35879.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35879
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
