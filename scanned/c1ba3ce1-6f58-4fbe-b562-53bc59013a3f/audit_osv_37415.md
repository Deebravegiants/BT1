# [H] can: raw: fix ro->uniq use-after-free in raw_rcv()

## Summary
Severity: High
Advisory: CVE-2026-31532
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-31532
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: raw: fix ro->uniq use-after-free in raw_rcv()

raw_release() unregisters raw CAN receive filters via can_rx_unregister(),
but receiver deletion is deferred with call_rcu(). This leaves a window
where raw_rcv() may still be running in an RCU read-side critical section
after raw_release() frees ro->uniq, leading to a use-after-free of the
percpu uniq storage.

Move free_percpu(ro->uniq) out of raw_release() and into a raw-specific
socket destructor. can_rx_unregister() takes an extra reference to the
socket and only drops it from the RCU callback, so freeing uniq from
sk_destruct ensures the percpu area is not released until the relevant
callbacks have drained.

[mkl: applied manually]

## References
- https://git.kernel.org/stable/c/1a0f2de81f7fbdc538fc72d7d74609b79bc83cc0
- https://git.kernel.org/stable/c/1de30576a6dfeaaa27ef91fa272e6b9240b6fbd3
- https://git.kernel.org/stable/c/34c1741254ff972e8375faf176678a248826fe3a
- https://git.kernel.org/stable/c/3f43f12fde34737fba091b7e3ab391e14ddbb0be
- https://git.kernel.org/stable/c/572f0bf536ebc14f6e7da3d21a85cf076de8358e
- https://git.kernel.org/stable/c/5e9cfffad898bbeaafd0ea608a6d267362f050fc
- https://git.kernel.org/stable/c/64c8553decf5a5f2417bd54761ea0a832c56c4ca
- https://git.kernel.org/stable/c/7201a531b9a5ed892bfda5ded9194ef622de8ffa
- https://git.kernel.org/stable/c/a535a9217ca3f2fccedaafb2fddb4c48f27d36dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31532.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31532
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
