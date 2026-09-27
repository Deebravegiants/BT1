# [M] powerpc/secvar: fix refcount leak in format_show()

## Summary
Severity: Medium
Advisory: CVE-2022-49113
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49113
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/secvar: fix refcount leak in format_show()

Refcount leak will happen when format_show returns failure in multiple
cases. Unified management of of_node_put can fix this problem.

## References
- https://git.kernel.org/stable/c/02222bf4f0a27f6eba66d1f597cdb5daadd51829
- https://git.kernel.org/stable/c/2a71e3ecd829a82013cf095c55068c61d991e885
- https://git.kernel.org/stable/c/c105ffb6b9744158e37e9f81f0f38861951d1c1f
- https://git.kernel.org/stable/c/d05e4265d33af60b39606c20c731e3e719bfe3d6
- https://git.kernel.org/stable/c/d601fd24e6964967f115f036a840f4f28488f63f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49113.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49113
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
