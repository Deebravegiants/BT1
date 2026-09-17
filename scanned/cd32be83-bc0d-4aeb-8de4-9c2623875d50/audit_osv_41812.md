# [H] xfrm: input: hold netns during deferred transport reinjection

## Summary
Severity: High
Advisory: CVE-2026-63919
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63919
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: input: hold netns during deferred transport reinjection

Transport-mode reinjection stores a struct net pointer in skb->cb and
uses it later from xfrm_trans_reinject(). That pointer must stay valid
until the deferred callback runs.

Take a netns reference when queueing deferred reinjection work and drop
it after the callback completes. Use maybe_get_net() so the queueing
path does not revive a namespace that is already being torn down.

This keeps the existing workqueue design and fixes the netns lifetime
handling in one place for all users of xfrm_trans_queue_net().

## References
- https://git.kernel.org/stable/c/2df7059a18afb7d3aee6c36cad5d371c198111d4
- https://git.kernel.org/stable/c/48ce101cd630d6745b6923b5bad8358bc4c119da
- https://git.kernel.org/stable/c/55ddfc41451f01c588089cd74957a05311b6f202
- https://git.kernel.org/stable/c/7ee59eda8820b758ed29e1cd3222359c7b97302c
- https://git.kernel.org/stable/c/8dfabcba6a943a7a02ebe1e1637c361ba96acbaa
- https://git.kernel.org/stable/c/9f67a36e91bb50d358760f381f233913fe5c09f8
- https://git.kernel.org/stable/c/9f7ebb45a83afc3216e855e57d51bb4bc9b5232e
- https://git.kernel.org/stable/c/c16f74dc1d75d0e2e7670076d5375deda110ebeb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63919.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63919
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
