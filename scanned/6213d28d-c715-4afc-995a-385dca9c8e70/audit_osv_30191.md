# [M] fsl/fman: Fix refcount handling of fman-related devices

## Summary
Severity: Medium
Advisory: CVE-2024-50166
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50166
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fsl/fman: Fix refcount handling of fman-related devices

In mac_probe() there are multiple calls to of_find_device_by_node(),
fman_bind() and fman_port_bind() which takes references to of_dev->dev.
Not all references taken by these calls are released later on error path
in mac_probe() and in mac_remove() which lead to reference leaks.

Add references release.

## References
- https://git.kernel.org/stable/c/1dec67e0d9fbb087c2ab17bf1bd17208231c3bb1
- https://git.kernel.org/stable/c/3c2a3619d565fe16bf59b0a047bab103a2ee4490
- https://git.kernel.org/stable/c/5ed4334fc9512f934fe2ae9c4cf7f8142e451b8b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50166.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50166
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
