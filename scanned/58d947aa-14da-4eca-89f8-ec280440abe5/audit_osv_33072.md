# [H] drm/xe: Make dma-fences compliant with the safe access rules

## Summary
Severity: High
Advisory: CVE-2025-38703
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38703
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Make dma-fences compliant with the safe access rules

Xe can free some of the data pointed to by the dma-fences it exports. Most
notably the timeline name can get freed if userspace closes the associated
submit queue. At the same time the fence could have been exported to a
third party (for example a sync_fence fd) which will then cause an use-
after-free on subsequent access.

To make this safe we need to make the driver compliant with the newly
documented dma-fence rules. Driver has to ensure a RCU grace period
between signalling a fence and freeing any data pointed to by said fence.

For the timeline name we simply make the queue be freed via kfree_rcu and
for the shared lock associated with multiple queues we add a RCU grace
period before freeing the per GT structure holding the lock.

## References
- https://git.kernel.org/stable/c/683b0e397dad9f26a42dcacf6f7f545a77ce6c06
- https://git.kernel.org/stable/c/6bd90e700b4285e6a7541e00f969cab0d696adde
- https://git.kernel.org/stable/c/b17fcce70733c211cb5dabf54f4f9491920b1d92
- https://git.kernel.org/stable/c/ba37807d08bae67de6139346a85650cab5f6145a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38703.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38703
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
