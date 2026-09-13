# [M] staging: vchiq_arm: Avoid NULL ptr deref in vchiq_dump_platform_instances

## Summary
Severity: Medium
Advisory: CVE-2022-49106
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49106
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: vchiq_arm: Avoid NULL ptr deref in vchiq_dump_platform_instances

vchiq_get_state() can return a NULL pointer. So handle this cases and
avoid a NULL pointer derefence in vchiq_dump_platform_instances.

## References
- https://git.kernel.org/stable/c/176df12b38c70b0a45e6392a0ee5bc83489dfc29
- https://git.kernel.org/stable/c/4627250cabaa80278d3ab01ad107893cea83799f
- https://git.kernel.org/stable/c/51e5e5c34c22c0bfec0808d8c33e0b2fcf4c7c89
- https://git.kernel.org/stable/c/aa899e686d442c63d50f4d369cc02dbbf0941cb0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49106.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49106
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
