# [M] ice: always check VF VSI pointer values

## Summary
Severity: Medium
Advisory: CVE-2022-49516
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49516
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: always check VF VSI pointer values

The ice_get_vf_vsi function can return NULL in some cases, such as if
handling messages during a reset where the VSI is being removed and
recreated.

Several places throughout the driver do not bother to check whether this
VSI pointer is valid. Static analysis tools maybe report issues because
they detect paths where a potentially NULL pointer could be dereferenced.

Fix this by checking the return value of ice_get_vf_vsi everywhere.

## References
- https://git.kernel.org/stable/c/baeb705fd6a7245cc1fa69ed991a9cffdf44a174
- https://git.kernel.org/stable/c/e7be3877589d539c52e5d1d23a625f889b541b9d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49516.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49516
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
