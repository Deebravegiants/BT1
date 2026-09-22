# [H] CVE-2021-47646

## Summary
Severity: High
Advisory: CVE-2021-47646
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47646
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "Revert "block, bfq: honor already-setup queue merges""

A crash [1] happened to be triggered in conjunction with commit
2d52c58b9c9b ("block, bfq: honor already-setup queue merges"). The
latter was then reverted by commit ebc69e897e17 ("Revert "block, bfq:
honor already-setup queue merges""). Yet, the reverted commit was not
the one introducing the bug. In fact, it actually triggered a UAF
introduced by a different commit, and now fixed by commit d29bd41428cf
("block, bfq: reset last_bfqq_created on group change").

So, there is no point in keeping commit 2d52c58b9c9b ("block, bfq:
honor already-setup queue merges") out. This commit restores it.

[1] https://bugzilla.kernel.org/show_bug.cgi?id=214503

## References
- https://git.kernel.org/stable/c/cc051f497eac9d8a0d816cd4bffa3415f2724871
- https://git.kernel.org/stable/c/f990f0985eda59d4f29fc83fcf300c92b1225d39
- https://git.kernel.org/stable/c/15729ff8143f8135b03988a100a19e66d7cb7ecd
- https://git.kernel.org/stable/c/4083925bd6dc89216d156474a8076feec904e607
- https://git.kernel.org/stable/c/65d8a737452e88f251fe5d925371de6d606df613
- https://git.kernel.org/stable/c/931aff627469a75c77b9fd3823146d0575afffd6
- https://git.kernel.org/stable/c/abc2129e646af7b43025d90a071f83043f1ae76c
