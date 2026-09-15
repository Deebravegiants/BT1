# [C] afs: Fix netns teardown to cancel the preallocation charger

## Summary
Severity: Critical
Advisory: CVE-2026-74427
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74427
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix netns teardown to cancel the preallocation charger

Fix the teardown of an afs network namespace to make sure it cancels the
work item that keeps the preallocated rxrpc call/conn/peer queue charged
before incoming calls are disabled (i.e. listen 0).

Also, if net->live is false because the afs netns is being deleted, make
afs_charge_preallocation() skip charging and make afs_rx_new_call() avoid
requeuing the charger.

(This was found by AI review).

## References
- https://git.kernel.org/stable/c/47694fbc9d24ab6bf210f91e8efe06a10a478064
- https://git.kernel.org/stable/c/59e8b7652f6cbfb62d377ead0ad553c1b4e39a7a
- https://git.kernel.org/stable/c/63ccaf1bdf8be2330f47f9b5b233dd3fd04acbd9
- https://git.kernel.org/stable/c/85d5fb80fe4f0cc836b6df83f26de204fe102ff7
- https://git.kernel.org/stable/c/a33975ff2b6ea47b8f29956403374b1cdd057539
- https://git.kernel.org/stable/c/b83ecf80e28afb7b6595ba79932e77ca68a5a83d
- https://git.kernel.org/stable/c/eec89c5f8e1adc1de4824042ef75f62aed804153
- https://git.kernel.org/stable/c/f5096e18b6b7fbd1c2a1942e275a51bcfdfb2ad1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74427.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74427
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
