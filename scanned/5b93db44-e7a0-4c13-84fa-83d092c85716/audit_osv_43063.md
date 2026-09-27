# [H] net: udp_tunnel: prevent double queueing in udp_tunnel_nic_device_sync

## Summary
Severity: High
Advisory: CVE-2026-72405
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72405
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: udp_tunnel: prevent double queueing in udp_tunnel_nic_device_sync

Yue Sun reported a use-after-free and debugobjects warning in
udp_tunnel_nic_device_sync_work() during concurrent device operations.

The workqueue core clears the internal pending bit before invoking the
worker. At that point, a concurrent thread can queue the work again.
When the already running worker eventually clears the work_pending flag
to 0, it mistakenly clears the flag for the newly queued instance.
udp_tunnel_nic_unregister() then observes work_pending as 0 and frees
the structure while the second work item is still active in the queue,
leading to UAF.

Fix this by returning early in udp_tunnel_nic_device_sync() if
work_pending is already set, preventing redundant work queueing.

## References
- https://git.kernel.org/stable/c/54292b167466cdf42176b7b6f01da66c184deb12
- https://git.kernel.org/stable/c/9075efb9b2c1d9d7a8285c937b64aa93ca0c41b7
- https://git.kernel.org/stable/c/cee6688e5731c0591643521716d1a1a5c1a98bf8
- https://git.kernel.org/stable/c/ecf69d4b43370c587e48d4d70289dbdb7e039d4d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72405.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72405
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
