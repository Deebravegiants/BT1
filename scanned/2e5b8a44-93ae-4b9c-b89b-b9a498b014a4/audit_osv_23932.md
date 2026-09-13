# [M] drm/msm/mdp4: Fix refcount leak in mdp4_modeset_init_intf

## Summary
Severity: Medium
Advisory: CVE-2022-49693
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49693
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.202, >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/mdp4: Fix refcount leak in mdp4_modeset_init_intf

of_graph_get_remote_node() returns remote device node pointer with
refcount incremented, we should use of_node_put() on it
when not need anymore.
Add missing of_node_put() to avoid refcount leak.

Patchwork: https://patchwork.freedesktop.org/patch/488473/

## References
- https://git.kernel.org/stable/c/3c39a17197733bc37786ed68c83267c2f491840b
- https://git.kernel.org/stable/c/b9cc4598607cb7f7eae5c75fc1e3209cd52ff5e0
- https://git.kernel.org/stable/c/d1592d3e362cc59b29f15019707b16c695d70ca3
- https://git.kernel.org/stable/c/d16a4339825e64f9ddcdff5277982d640bae933b
- https://git.kernel.org/stable/c/d607da76fd2b1cf1d377af9d9b7c6f8fecbb0e1d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49693.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49693
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
