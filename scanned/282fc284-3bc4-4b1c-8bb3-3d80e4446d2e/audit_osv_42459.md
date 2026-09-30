# [H] misc: nsm: only unlock nsm_dev on post-lock error paths

## Summary
Severity: High
Advisory: CVE-2026-68179
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68179
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: nsm: only unlock nsm_dev on post-lock error paths

nsm_dev_ioctl() jumps to the common out label even when the initial
copy_from_user() fails before nsm->lock has been taken.  The error path
then blindly unlocks a mutex that was never acquired.

This issue was found by our static analysis tool and then manually
reviewed against the current tree.

The grounded PoC kept the miscdevice ioctl entry and the pre-lock
copy_from_user(&raw, argp, _IOC_SIZE(cmd)) failure path by issuing
NSM_IOCTL_RAW with an invalid user pointer.  That failure reaches the
shared out label before mutex_lock(&nsm->lock).  Lockdep reported:

  WARNING: bad unlock balance detected!
  exploit/193 is trying to release lock (&global_nsm.lock) at:
  nsm_dev_ioctl+0x5f/0xcf [vuln_msv]
  but there are no more locks to release!
  no locks held by exploit/193.

Return immediately on the pre-lock copy_from_user() failure and keep the
common unlock label for the post-lock paths only.

## References
- https://git.kernel.org/stable/c/4aa3f7d48e91eb74a363c1b4d7dbdd28f5b341fb
- https://git.kernel.org/stable/c/8f068342096b027181b168d91fef7ac7a2c64b25
- https://git.kernel.org/stable/c/ce1fed11d18e163baf7f875152a33bf80f625c1a
- https://git.kernel.org/stable/c/f318f5a872cb9096536e759b23ae5c9873bb80ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68179.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68179
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
