# [M] ath11k: add missing of_node_put() to avoid leak

## Summary
Severity: Medium
Advisory: CVE-2022-49237
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49237
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ath11k: add missing of_node_put() to avoid leak

The node pointer is returned by of_find_node_by_type()
or of_parse_phandle() with refcount incremented. Calling
of_node_put() to aovid the refcount leak.

## References
- https://git.kernel.org/stable/c/3d38faef0de1756994b3d95e47b2302842f729e2
- https://git.kernel.org/stable/c/7d51cb010b20d70b16dc6e4341bf29d6c5b32564
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49237.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49237
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
