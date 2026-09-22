# [H] mac802154: fix netdev use-after-free in beacon worker

## Summary
Severity: High
Advisory: CVE-2026-74661
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74661
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac802154: fix netdev use-after-free in beacon worker

mac802154_beacon_worker() reads local->beacon_req under RCU and derives
the sub-interface from the request, but then drops the RCU read lock and
continues to use both sdata and the embedded wpan_dev.

mac802154_stop_beacons_locked() cancels only pending beacon work, clears
local->beacon_req and frees the request.  A beacon worker that is already
running can therefore continue after interface teardown and dereference
the freed netdev private area.

The scan worker already pins the netdev before leaving RCU.  Apply the
same lifetime rule to the beacon worker: take a netdev reference while
the request is still protected by RCU, and release it on all paths that
continue after the reference is acquired.

## References
- https://git.kernel.org/stable/c/5f26a690e8efa54315e4922368daf54e0b8f5515
- https://git.kernel.org/stable/c/9d067e581597c462c51fee8a30b51bc48a68c4e1
- https://git.kernel.org/stable/c/e5fb0e03bc7f45508c182a427357bf6b389a9033
- https://git.kernel.org/stable/c/e6cd416a899edc912b428c4ba399bd73f516cb31
- https://git.kernel.org/stable/c/fe820dcc1d8ff77783a9d2bcc93b98c99ac6d517
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74661.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74661
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
