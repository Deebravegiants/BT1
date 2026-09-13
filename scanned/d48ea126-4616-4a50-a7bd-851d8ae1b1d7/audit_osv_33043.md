# [H] eventpoll: Fix semi-unbounded recursion

## Summary
Severity: High
Advisory: CVE-2025-38614
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38614
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

eventpoll: Fix semi-unbounded recursion

Ensure that epoll instances can never form a graph deeper than
EP_MAX_NESTS+1 links.

Currently, ep_loop_check_proc() ensures that the graph is loop-free and
does some recursion depth checks, but those recursion depth checks don't
limit the depth of the resulting tree for two reasons:

 - They don't look upwards in the tree.
 - If there are multiple downwards paths of different lengths, only one of
   the paths is actually considered for the depth check since commit
   28d82dc1c4ed ("epoll: limit paths").

Essentially, the current recursion depth check in ep_loop_check_proc() just
serves to prevent it from recursing too deeply while checking for loops.

A more thorough check is done in reverse_path_check() after the new graph
edge has already been created; this checks, among other things, that no
paths going upwards from any non-epoll file with a length of more than 5
edges exist. However, this check does not apply to non-epoll files.

As a result, it is possible to recurse to a depth of at least roughly 500,
tested on v6.15. (I am unsure if deeper recursion is possible; and this may
have changed with commit 8c44dac8add7 ("eventpoll: Fix priority inversion
problem").)

To fix it:

1. In ep_loop_check_proc(), note the subtree depth of each visited node,
and use subtree depths for the total depth calculation even when a subtree
has already been visited.
2. Add ep_get_upwards_depth_proc() for similarly determining the maximum
depth of an upwards walk.
3. In ep_loop_check(), use these values to limit the total path length
between epoll nodes to EP_MAX_NESTS edges.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1b13b033062824495554e836a1ff5f85ccf6b039
- https://git.kernel.org/stable/c/2a0c0c974bea9619c6f41794775ae4b97530e0e6
- https://git.kernel.org/stable/c/3542c90797bc3ab83ebab54b737d751cf3682036
- https://git.kernel.org/stable/c/71379495ab70eaba19224bd71b5b9b399eb85e04
- https://git.kernel.org/stable/c/7a2125962c42d5336ca0495a9ce4cb38a63e9161
- https://git.kernel.org/stable/c/ea5f97dbdcb1651581a22bd10afd2f0dd9dc11d6
- https://git.kernel.org/stable/c/f2e467a48287c868818085aa35389a224d226732
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38614.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38614
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
