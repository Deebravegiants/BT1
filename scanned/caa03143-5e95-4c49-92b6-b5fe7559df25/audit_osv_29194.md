# [H] drm/i915/dpt: Make DPT object unshrinkable

## Summary
Severity: High
Advisory: CVE-2024-40924
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40924
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/dpt: Make DPT object unshrinkable

In some scenarios, the DPT object gets shrunk but
the actual framebuffer did not and thus its still
there on the DPT's vm->bound_list. Then it tries to
rewrite the PTEs via a stale CPU mapping. This causes panic.

[vsyrjala: Add TODO comment]
(cherry picked from commit 51064d471c53dcc8eddd2333c3f1c1d9131ba36c)

## References
- https://git.kernel.org/stable/c/327280149066f0e5f2e50356b5823f76dabfe86e
- https://git.kernel.org/stable/c/43e2b37e2ab660c3565d4cff27922bc70e79c3f1
- https://git.kernel.org/stable/c/7a9883be3b98673333eec65c4a21cc18e60292eb
- https://git.kernel.org/stable/c/a2552020fb714ff357182c3c179abfac2289f84d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40924.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
