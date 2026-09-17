# [C] gfs2: Fix potential glock use-after-free on unmount

## Summary
Severity: Critical
Advisory: CVE-2024-38570
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38570
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: Fix potential glock use-after-free on unmount

When a DLM lockspace is released and there ares still locks in that
lockspace, DLM will unlock those locks automatically.  Commit
fb6791d100d1b started exploiting this behavior to speed up filesystem
unmount: gfs2 would simply free glocks it didn't want to unlock and then
release the lockspace.  This didn't take the bast callbacks for
asynchronous lock contention notifications into account, which remain
active until until a lock is unlocked or its lockspace is released.

To prevent those callbacks from accessing deallocated objects, put the
glocks that should not be unlocked on the sd_dead_glocks list, release
the lockspace, and only then free those glocks.

As an additional measure, ignore unexpected ast and bast callbacks if
the receiving glock is dead.

## References
- https://git.kernel.org/stable/c/0636b34b44589b142700ac137b5f69802cfe2e37
- https://git.kernel.org/stable/c/501cd8fabf621d10bd4893e37f6ce6c20523c8ca
- https://git.kernel.org/stable/c/d98779e687726d8f8860f1c54b5687eec5f63a73
- https://git.kernel.org/stable/c/e42e8a24d7f02d28763d16ca7ec5fc6d1f142af0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38570.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
