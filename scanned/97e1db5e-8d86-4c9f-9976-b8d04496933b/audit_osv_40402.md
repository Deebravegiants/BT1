# [H] drm/gem: Try to fix change_handle ioctl, attempt 4

## Summary
Severity: High
Advisory: CVE-2026-53145
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53145
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.32 <6.18.36, >=7.0.9 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/gem: Try to fix change_handle ioctl, attempt 4

[airlied: just added some comments on how to reenable]
On-list because the cat is out of the bag and we're clearly not good
enough to figure this out in private. The story thus far:

5e28b7b94408 ("drm: Set old handle to NULL before prime swap in
change_handle") tried to fix a race condition between the gem_close and
gem_change_handle ioctls, but got a few things wrong:

- There's a confusion with the local variable handle, which is actually
  the new handle, and so the two-stage trick was actually applied to the
  wrong idr slot. 7164d78559b0 ("drm/gem: fix race between
  change_handle and handle_delete") tried to fix that by adding yet
  another code block, but forgot to add the error handling. Which meant
  we now have two paths, both kinda wrong.

- dc366607c41c ("drm: Replace old pointer to new idr") tried to apply
  another fix, but inconsistently, again because of the handle confusion
  - this would be the right fix (kinda, somewhat, it's a mess) if we'd
  do the two-stage approach for the new handle. Except that wasn't the
  intent of the original fix.

We also didn't have an igt merged for the original ioctl, which is a big
no-go. This was attempted to address off-list in the original bugfix,
and amd QA people claimed the bug was fixed now. Very clearly that's not
the case. Here's my attempt to sort this out:

- Rename the local variable to new_handle, the old aliasing with
  args->handle is just too dangerously confusing.

- Merge the gem obj lookup with the two-stage idr_replace so that we
  avoid getting ourselves confused there.

- This means we don't have a surplus temporary reference anymore, only
  an inherited from the idr. A concurrent gem_close on the new_handle
  could steal that. Fix that with the same two-stage approach
  create_tail uses. This is a bit overkill as documented in the comment,
  but I also don't trust my ability to understand this all correctly, so
  go with the established pattern we have from other ioctls instead for
  maximum paranoia.

- Adjust error paths. I've tried to make the error and success paths
  common, because they are identical except for which handle is removed
  and on which we call idr_replace to (re)install the object again. But
  that made things messier to read, so I've left it at the more verbose
  version, which unfortunately hides the symmetry in the entire code
  flow a bit.

- While at it, also replace the 7 space indent with 1 tab.

And finally, because I flat out don't trust my abilities here at all
anymore:

- Disable the ioctl until we have the igt situation and everything else
  sorted out on-list and with full consensus.

v2:

Sashiko noticed that I didn't handle the error path for idr_replace
correctly, it must be checked with IS_ERR_OR_NULL like in
gem_handle_delete. So yeah, definitely should just the existing paths
1:1 because this is endless amounts of tricky.

Also add the Fixes: line for the original ioctl, I forgot that too.

## References
- https://git.kernel.org/stable/c/1a4f03d22fb655e5f192244fb2c87d8066fcfca2
- https://git.kernel.org/stable/c/1d9b93df7fc768228906e24220591ec1cddad391
- https://git.kernel.org/stable/c/c0639ede2f24ac224b2079cd35ecd5fd8ad4e3cd
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53145.json
- https://access.redhat.com/security/cve/CVE-2026-53145
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53145.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53145
- https://bugzilla.redhat.com/show_bug.cgi?id=2492773
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
