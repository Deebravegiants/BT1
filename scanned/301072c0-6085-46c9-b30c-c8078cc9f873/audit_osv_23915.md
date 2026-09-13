# [M] PM / devfreq: exynos-ppmu: Fix refcount leak in of_get_devfreq_events

## Summary
Severity: Medium
Advisory: CVE-2022-49668
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49668
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.4.204, >=5.5.0 <5.10.129, >=5.11.0 <5.15.53, >=5.16.0 <5.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

PM / devfreq: exynos-ppmu: Fix refcount leak in of_get_devfreq_events

of_get_child_by_name() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
This function only calls of_node_put() in normal path,
missing it in error paths.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/01121e39ef537289926ae6f5374dce92c796d863
- https://git.kernel.org/stable/c/194781229d4cbc804b8ded13156eb8addce87d6c
- https://git.kernel.org/stable/c/bdecd912e99acfd61507f1720d3f4eed1b3418d8
- https://git.kernel.org/stable/c/e65027fdebbacd40595e96ef7b5d2418f71bddf2
- https://git.kernel.org/stable/c/f44b799603a9b5d2e375b0b2d54dd0b791eddfc2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49668.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49668
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
