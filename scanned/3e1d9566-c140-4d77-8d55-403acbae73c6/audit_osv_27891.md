# [H] dm-crypt, dm-verity: disable tasklets

## Summary
Severity: High
Advisory: CVE-2024-26718
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26718
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.169, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-crypt, dm-verity: disable tasklets

Tasklets have an inherent problem with memory corruption. The function
tasklet_action_common calls tasklet_trylock, then it calls the tasklet
callback and then it calls tasklet_unlock. If the tasklet callback frees
the structure that contains the tasklet or if it calls some code that may
free it, tasklet_unlock will write into free memory.

The commits 8e14f610159d and d9a02e016aaf try to fix it for dm-crypt, but
it is not a sufficient fix and the data corruption can still happen [1].
There is no fix for dm-verity and dm-verity will write into free memory
with every tasklet-processed bio.

There will be atomic workqueues implemented in the kernel 6.9 [2]. They
will have better interface and they will not suffer from the memory
corruption problem.

But we need something that stops the memory corruption now and that can be
backported to the stable kernels. So, I'm proposing this commit that
disables tasklets in both dm-crypt and dm-verity. This commit doesn't
remove the tasklet support, because the tasklet code will be reused when
atomic workqueues will be implemented.

[1] https://lore.kernel.org/all/d390d7ee-f142-44d3-822a-87949e14608b@suse.de/T/
[2] https://lore.kernel.org/lkml/20240130091300.2968534-1-tj@kernel.org/

## References
- https://git.kernel.org/stable/c/0a9bab391e336489169b95cb0d4553d921302189
- https://git.kernel.org/stable/c/0c45a20cbe68bc4d681734f5c03891124a274257
- https://git.kernel.org/stable/c/30884a44e0cedc3dfda8c22432f3ba4078ec2d94
- https://git.kernel.org/stable/c/5735a2671ffb70ea29ca83969fe01316ee2ed6fc
- https://git.kernel.org/stable/c/b825e0f9d68c178072bffd32dd34c39e3d2d597a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26718.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26718
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
