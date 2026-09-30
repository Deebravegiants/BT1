# [M] rhashtable: Fix potential deadlock by moving schedule_work outside lock

## Summary
Severity: Medium
Advisory: CVE-2024-58042
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58042
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rhashtable: Fix potential deadlock by moving schedule_work outside lock

Move the hash table growth check and work scheduling outside the
rht lock to prevent a possible circular locking dependency.

The original implementation could trigger a lockdep warning due to
a potential deadlock scenario involving nested locks between
rhashtable bucket, rq lock, and dsq lock. By relocating the
growth check and work scheduling after releasing the rth lock, we break
this potential deadlock chain.

This change expands the flexibility of rhashtable by removing
restrictive locking that previously limited its use in scheduler
and workqueue contexts.

Import to say that this calls rht_grow_above_75(), which reads from
struct rhashtable without holding the lock, if this is a problem, we can
move the check to the lock, and schedule the workqueue after the lock.


Modified so that atomic_inc is also moved outside of the bucket
lock along with the growth above 75% check.

## References
- https://git.kernel.org/stable/c/ced8ce3c83a7150c5f5d371a8c332d7bc7f9b66d
- https://git.kernel.org/stable/c/e1d3422c95f003eba241c176adfe593c33e8a8f6
- https://git.kernel.org/stable/c/eb2e58484b838fb4e777ee9721bb9e20e6ca971d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58042.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58042
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
