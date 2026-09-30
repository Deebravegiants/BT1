# [H] net: openvswitch: reject oversized nested action attrs

## Summary
Severity: High
Advisory: CVE-2026-64531
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64531
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.14.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: openvswitch: reject oversized nested action attrs

Open vSwitch stores generated flow actions as nlattrs, whose nla_len
field is u16. Commit a1e64addf3ff ("net: openvswitch: remove
misbehaving actions length check") allowed the total sw_flow_actions
stream to grow beyond 64 KiB, which is valid, but also removed the last
guard preventing a generated nested action attribute from exceeding
U16_MAX.

An oversized generated container can thus be closed with a truncated
nla_len. A later dump or teardown then walks a structurally different
stream than the one that was validated. In particular, an oversized
nested CLONE/CT action may cause subsequent bytes in the generated
stream to be interpreted as independent actions.

Keep the larger total-action-stream behavior, but make nested action
close reject generated containers that do not fit in nla_len, and return
the error through all callers. For recursive SAMPLE, CLONE, DEC_TTL, and
CHECK_PKT_LEN builders, trim resource-owning action-list tails in reverse
construction order before discarding failed wrappers, so resources copied
into the rejected tails are released before the wrappers are removed.

Most failed outer wrappers are discarded by truncating actions_len after
child resources have been released. CHECK_PKT_LEN also trims its parent
after branch resources are gone. SET/TUNNEL close failures unwind their
known tun_dst ownership directly, and SET_TO_MASKED has no external
ownership and truncates on close failure.

## References
- http://www.openwall.com/lists/oss-security/2026/07/28/8
- http://www.openwall.com/lists/oss-security/2026/07/31/17
- http://www.openwall.com/lists/oss-security/2026/08/01/1
- http://www.openwall.com/lists/oss-security/2026/08/01/3
- http://www.openwall.com/lists/oss-security/2026/08/22/1
- https://git.kernel.org/stable/c/1b41cbe05b184f8861712f0806cc0c4f5d8c6dfe
- https://git.kernel.org/stable/c/3f1f755366687d051174739fb99f7d560202f60b
- https://git.kernel.org/stable/c/ab855641241387db062a5e41d9ad6b8561542572
- https://git.kernel.org/stable/c/c66bd2626c2764f23764ff0f8277f44a9cfe8349
- https://git.kernel.org/stable/c/d573250d228401f707f4dbc09d11227a6215ee5f
- https://git.kernel.org/stable/c/dbd14f736be02cfe73049bd801af89becd1a0749
- https://git.kernel.org/stable/c/f1efff8858403191361a01269c6fe8dd7f55a385
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64531.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64531
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
