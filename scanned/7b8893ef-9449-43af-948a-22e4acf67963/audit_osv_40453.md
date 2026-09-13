# [H] xfrm: policy: fix use-after-free on inexact bin in xfrm_policy_bysel_ctx()

## Summary
Severity: High
Advisory: CVE-2026-53239
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53239
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: policy: fix use-after-free on inexact bin in xfrm_policy_bysel_ctx()

Fix the race by pruning the bin while still holding xfrm_policy_lock,
before dropping it. Use __xfrm_policy_inexact_prune_bin() directly since
the lock is already held. The wrapper xfrm_policy_inexact_prune_bin()
becomes unused and is removed.

Race:

  CPU0 (XFRM_MSG_DELPOLICY)           CPU1 (XFRM_MSG_NEWSPDINFO)
  ==========================          ==========================
  xfrm_policy_bysel_ctx():
    spin_lock_bh(xfrm_policy_lock)
    bin = xfrm_policy_inexact_lookup()
    __xfrm_policy_unlink(pol)
    spin_unlock_bh(xfrm_policy_lock)
    xfrm_policy_kill(ret)
    // wide window, lock not held
                                       xfrm_hash_rebuild():
                                         spin_lock_bh(xfrm_policy_lock)
                                         __xfrm_policy_inexact_flush():
                                           kfree_rcu(bin)  // bin freed
                                         spin_unlock_bh(xfrm_policy_lock)
    xfrm_policy_inexact_prune_bin(bin)
    // UAF: bin is freed

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/25c8c7fb3b0b9668c7d05e209f58c158d2b020c7
- https://git.kernel.org/stable/c/42827d03f8009a6a218bacab153e21f39d6a121c
- https://git.kernel.org/stable/c/7f2d76c9c03257c0782afef9d95321fa04096f60
- https://git.kernel.org/stable/c/88697cf980222d5906a37bf47662dac0732e2a0f
- https://git.kernel.org/stable/c/8fc536e9f6856230f19c7d13e71af064b6a77b22
- https://git.kernel.org/stable/c/b5316e2b8614a87d8736941972441cb47bfd4491
- https://git.kernel.org/stable/c/c4c1ea36d83bf3c4569468ca5b8b614fda1bf821
- https://git.kernel.org/stable/c/ec82ea4eb220164d854f8734ca5a35e23e577b94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53239.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
