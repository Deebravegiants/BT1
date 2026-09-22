# [M] CVE-2021-47360

## Summary
Severity: Medium
Advisory: CVE-2021-47360
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47360
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: make sure fd closes complete

During BC_FREE_BUFFER processing, the BINDER_TYPE_FDA object
cleanup may close 1 or more fds. The close operations are
completed using the task work mechanism -- which means the thread
needs to return to userspace or the file object may never be
dereferenced -- which can lead to hung processes.

Force the binder thread back to userspace if an fd is closed during
BC_FREE_BUFFER handling.

## References
- https://git.kernel.org/stable/c/5fdb55c1ac9585eb23bb2541d5819224429e103d
- https://git.kernel.org/stable/c/aa2c274c279ff365a06a4cba263f04965895166e
- https://git.kernel.org/stable/c/b95483d8d94b41fa31a84c1d86710b7907a37621
- https://git.kernel.org/stable/c/d5b0473707fa53b03a5db0256ce62b2874bddbc7
