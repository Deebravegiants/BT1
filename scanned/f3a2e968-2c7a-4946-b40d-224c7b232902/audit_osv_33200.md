# [H] drm/mediatek: fix potential OF node use-after-free

## Summary
Severity: High
Advisory: CVE-2025-39882
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39882
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.105 <6.6.107, >=6.12.45 <6.12.48, >=6.16.5 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mediatek: fix potential OF node use-after-free

The for_each_child_of_node() helper drops the reference it takes to each
node as it iterates over children and an explicit of_node_put() is only
needed when exiting the loop early.

Drop the recently introduced bogus additional reference count decrement
at each iteration that could potentially lead to a use-after-free.

## References
- https://git.kernel.org/stable/c/4de37a48b6b58faaded9eb765047cf0d8785ea18
- https://git.kernel.org/stable/c/b2fbe0f9f80b9cfa1e06ddcf8b863d918394ef1d
- https://git.kernel.org/stable/c/b58a26cdd4795c1ce6a80e38e9348885555dacd6
- https://git.kernel.org/stable/c/c4901802ed1ce859242e10af06e6a7752cba0497
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39882.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39882
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
