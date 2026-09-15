# [H] drm/panthor: fix for dma-fence safe access rules

## Summary
Severity: High
Advisory: CVE-2025-71302
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2025-71302
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: fix for dma-fence safe access rules

Commit 506aa8b02a8d6 ("dma-fence: Add safe access helpers and document
the rules") details the dma-fence safe access rules. The most common
culprit is that drm_sched_fence_get_timeline_name may race with
group_free_queue.

## References
- https://git.kernel.org/stable/c/ab8c0de60f16d7e0b162ccbbb35fcf1f277c97c2
- https://git.kernel.org/stable/c/eae60933abd11df013876f647c9edbd35ce67615
- https://git.kernel.org/stable/c/efe24898485c5c831e629d9c6fb9350c35cb576f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71302.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
