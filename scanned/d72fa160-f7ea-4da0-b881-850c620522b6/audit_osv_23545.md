# [M] staging: vchiq_core: handle NULL result of find_service_by_handle

## Summary
Severity: Medium
Advisory: CVE-2022-49104
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49104
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: vchiq_core: handle NULL result of find_service_by_handle

In case of an invalid handle the function find_servive_by_handle
returns NULL. So take care of this and avoid a NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/04202f54dd8899e10f56a89c4c1ede0043fa22af
- https://git.kernel.org/stable/c/3b424f6586a870b8d657c5e5419465bbe0e7b61f
- https://git.kernel.org/stable/c/42f2142a337ee372455574809fc924580a7e51b2
- https://git.kernel.org/stable/c/aa0b7296785312a4bfa8fac0ba8ad78698fd9fcf
- https://git.kernel.org/stable/c/ca225857faf237234d2fffe5d1919467dfadd822
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49104.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49104
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
