# [H] net/mlx5: Add a timeout to acquire the command queue semaphore

## Summary
Severity: High
Advisory: CVE-2024-38556
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38556
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Add a timeout to acquire the command queue semaphore

Prevent forced completion handling on an entry that has not yet been
assigned an index, causing an out of bounds access on idx = -22.
Instead of waiting indefinitely for the sem, blocking flow now waits for
index to be allocated or a sem acquisition timeout before beginning the
timer for FW completion.

Kernel log example:
mlx5_core 0000:06:00.0: wait_func_handle_exec_timeout:1128:(pid 185911): cmd[-22]: CREATE_UCTX(0xa04) No done completion

## References
- https://git.kernel.org/stable/c/2d0962d05c93de391ce85f6e764df895f47c8918
- https://git.kernel.org/stable/c/485d65e1357123a697c591a5aeb773994b247ad7
- https://git.kernel.org/stable/c/4baae687a20ef2b82fde12de3c04461e6f2521d6
- https://git.kernel.org/stable/c/94024332a129c6e4275569d85c0c1bfb2ae2d71b
- https://git.kernel.org/stable/c/f9caccdd42e999b74303c9b0643300073ed5d319
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38556.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38556
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
