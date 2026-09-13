# [C] xfrm: Fix xfrm state cache insertion race

## Summary
Severity: Critical
Advisory: CVE-2026-72451
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72451
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.97, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: Fix xfrm state cache insertion race

The xfrm input state cache insertion code checks the validity of
the state before acquiring the global xfrm_state_lock.  Thus it's
possible for someone else to kill the state after it passed the
validity check, and then the insertion will add the dead state
to the cache.

Fix this by moving the validity check inside the lock.

This entire function is called on the input path, where BH must
be off (e.g., the caller of this function xfrm_input acquires
its spinlocks without disabling BH).

So there is no need to disable BH here or take the RCU read lock.
Remove both and replace them with an assertion that trips if BH
is accidentally enabled on some future calling path.

## References
- https://git.kernel.org/stable/c/041859fd55c81ea55e76d051e39b7b79975b8c7d
- https://git.kernel.org/stable/c/6dab4dec9a49121d079981ac913569f232c06b06
- https://git.kernel.org/stable/c/a1a3360a0c44b8b5c134db2a9d0667b61c9cf523
- https://git.kernel.org/stable/c/ddd3d0132920319ac426e12456013eadbae67e15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72451.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72451
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
