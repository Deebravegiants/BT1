# [H] firmware: arm_scpi: Ensure scpi_info is not assigned if the probe fails

## Summary
Severity: High
Advisory: CVE-2022-50087
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50087
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.19.256, >=4.20.0 <5.4.211, >=5.5.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: arm_scpi: Ensure scpi_info is not assigned if the probe fails

When scpi probe fails, at any point, we need to ensure that the scpi_info
is not set and will remain NULL until the probe succeeds. If it is not
taken care, then it could result use-after-free as the value is exported
via get_scpi_ops() and could refer to a memory allocated via devm_kzalloc()
but freed when the probe fails.

## References
- https://git.kernel.org/stable/c/08272646cd7c310642c39b7f54348fddd7987643
- https://git.kernel.org/stable/c/0c29e149b6bb498778ed8a1c9597b51acfba7856
- https://git.kernel.org/stable/c/18048cba444a7c41dbf42c180d6b46606fc24c51
- https://git.kernel.org/stable/c/4f2d7b46d6b53c07f44a4f8f8f4438888f0e9e87
- https://git.kernel.org/stable/c/5aa558232edc30468d1f35108826dd5b3ffe978f
- https://git.kernel.org/stable/c/689640efc0a2c4e07e6f88affe6d42cd40cc3f85
- https://git.kernel.org/stable/c/87c4896d5dd7fd9927c814cf3c6289f41de3b562
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50087.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
