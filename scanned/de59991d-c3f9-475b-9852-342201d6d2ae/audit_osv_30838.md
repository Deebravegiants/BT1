# [M] scsi: ufs: core: sysfs: Prevent div by zero

## Summary
Severity: Medium
Advisory: CVE-2024-56622
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56622
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ufs: core: sysfs: Prevent div by zero

Prevent a division by 0 when monitoring is not enabled.

## References
- https://git.kernel.org/stable/c/0069928727c2e95ca26c738fbe6e4b241aeaaf08
- https://git.kernel.org/stable/c/7b21233e5f72d10f08310689f993c1dbdfde9f2c
- https://git.kernel.org/stable/c/87bf3ea841a5d77beae6bb85af36b2b3848407ee
- https://git.kernel.org/stable/c/9c191055c7abea4912fdb83cb9b261732b25a0c8
- https://git.kernel.org/stable/c/eb48e9fc0028bed94a40a9352d065909f19e333c
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56622.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56622
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
