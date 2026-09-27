# [H] devlink: fix possible use-after-free and memory leaks in devlink_init()

## Summary
Severity: High
Advisory: CVE-2024-26734
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26734
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

devlink: fix possible use-after-free and memory leaks in devlink_init()

The pernet operations structure for the subsystem must be registered
before registering the generic netlink family.

Make an unregister in case of unsuccessful registration.

## References
- https://git.kernel.org/stable/c/919092bd5482b7070ae66d1daef73b600738f3a2
- https://git.kernel.org/stable/c/def689fc26b9a9622d2e2cb0c4933dd3b1c8071c
- https://git.kernel.org/stable/c/e91d3561e28d7665f4f837880501dc8755f635a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26734.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26734
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
