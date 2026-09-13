# [H] CVE-2021-47533

## Summary
Severity: High
Advisory: CVE-2021-47533
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47533
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vc4: kms: Clear the HVS FIFO commit pointer once done

Commit 9ec03d7f1ed3 ("drm/vc4: kms: Wait on previous FIFO users before a
commit") introduced a wait on the previous commit done on a given HVS
FIFO.

However, we never cleared that pointer once done. Since
drm_crtc_commit_put can free the drm_crtc_commit structure directly if
we were the last user, this means that it can lead to a use-after free
if we were to duplicate the state, and that stale pointer would even be
copied to the new state.

Set the pointer to NULL once we're done with the wait so that we don't
carry over a pointer to a free'd structure.

## References
- https://git.kernel.org/stable/c/2931db9a5ed219546cf2ae0546698faf78281b89
- https://git.kernel.org/stable/c/d134c5ff71c7f2320fc7997f2fbbdedf0c76889a
