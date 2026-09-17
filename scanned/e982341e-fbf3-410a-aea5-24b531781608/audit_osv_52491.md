# [H] CVE-2021-47506

## Summary
Severity: High
Advisory: CVE-2021-47506
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47506
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix use-after-free due to delegation race

A delegation break could arrive as soon as we've called vfs_setlease.  A
delegation break runs a callback which immediately (in
nfsd4_cb_recall_prepare) adds the delegation to del_recall_lru.  If we
then exit nfs4_set_delegation without hashing the delegation, it will be
freed as soon as the callback is done with it, without ever being
removed from del_recall_lru.

Symptoms show up later as use-after-free or list corruption warnings,
usually in the laundromat thread.

I suspect aba2072f4523 "nfsd: grant read delegations to clients holding
writes" made this bug easier to hit, but I looked as far back as v3.0
and it looks to me it already had the same problem.  So I'm not sure
where the bug was introduced; it may have been there from the beginning.

## References
- https://git.kernel.org/stable/c/04a8d07f3d58308b92630045560799a3faa3ebce
- https://git.kernel.org/stable/c/148c816f10fd11df27ca6a9b3238cdd42fa72cd3
- https://git.kernel.org/stable/c/2becaa990b93cbd2928292c0b669d3abb6cf06d4
- https://git.kernel.org/stable/c/33645d3e22720cac1e4548f8fef57bf0649536ee
- https://git.kernel.org/stable/c/348714018139c39533c55661a0c7c990671396b4
- https://git.kernel.org/stable/c/548ec0805c399c65ed66c6641be467f717833ab5
- https://git.kernel.org/stable/c/e0759696de6851d7536efddfdd2dfed4c4df1f09
- https://git.kernel.org/stable/c/eeb0711801f5e19ef654371b627682aed3b11373
