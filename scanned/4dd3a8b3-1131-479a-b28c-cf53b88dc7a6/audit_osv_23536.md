# [H] drbd: Fix five use after free bugs in get_initial_state

## Summary
Severity: High
Advisory: CVE-2022-49085
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49085
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drbd: Fix five use after free bugs in get_initial_state

In get_initial_state, it calls notify_initial_state_done(skb,..) if
cb->args[5]==1. If genlmsg_put() failed in notify_initial_state_done(),
the skb will be freed by nlmsg_free(skb).
Then get_initial_state will goto out and the freed skb will be used by
return value skb->len, which is a uaf bug.

What's worse, the same problem goes even further: skb can also be
freed in the notify_*_state_change -> notify_*_state calls below.
Thus 4 additional uaf bugs happened.

My patch lets the problem callee functions: notify_initial_state_done
and notify_*_state_change return an error code if errors happen.
So that the error codes could be propagated and the uaf bugs can be avoid.

v2 reports a compilation warning. This v3 fixed this warning and built
successfully in my local environment with no additional warnings.
v2: https://lore.kernel.org/patchwork/patch/1435218/

## References
- https://git.kernel.org/stable/c/0489700bfeb1e53eb2039c2291c67e71b0b40103
- https://git.kernel.org/stable/c/188fe6b26765edbad4055611c0f788b6870f4024
- https://git.kernel.org/stable/c/226e993c39405292781bfcf4b039a8db56aab362
- https://git.kernel.org/stable/c/594205b4936771a250f9d141e7e0fff21c3dd2d9
- https://git.kernel.org/stable/c/a972c768723359ec995579902473028fe3cd64b1
- https://git.kernel.org/stable/c/aadb22ba2f656581b2f733deb3a467c48cc618f6
- https://git.kernel.org/stable/c/b6a4055036eed1f5e239ce3d8b0db1ce38bba447
- https://git.kernel.org/stable/c/dcf6be17b5c53b741898d2223b23e66d682de300
- https://git.kernel.org/stable/c/de63e74da2333b4068bb79983e632db730fea97e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49085.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49085
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
