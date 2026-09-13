# [M] drm/amdkfd: Dereference null return value

## Summary
Severity: Medium
Advisory: CVE-2024-56666
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56666
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Dereference null return value

In the function pqm_uninit there is a call-assignment of "pdd =
kfd_get_process_device_data" which could be null, and this value was
later dereferenced without checking.

## References
- https://git.kernel.org/stable/c/768442d918932c4da09003f1fd6be1750b93a4ba
- https://git.kernel.org/stable/c/a592bb19abdc2072875c87da606461bfd7821b08
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56666.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56666
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
