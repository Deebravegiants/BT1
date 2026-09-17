# [H] drm/amd/display: fix array index out of bound error in DCN32 DML

## Summary
Severity: High
Advisory: CVE-2022-48979
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48979
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: fix array index out of bound error in DCN32 DML

[Why&How]
LinkCapacitySupport array is indexed with the number of voltage states and
not the number of max DPPs. Fix the error by changing the array
declaration to use the correct (larger) array size of total number of
voltage states.

## References
- https://git.kernel.org/stable/c/3d8a298b2e83b98042e6ec726e934f535b23e6aa
- https://git.kernel.org/stable/c/aeffc8fb2174f017a10df114bc312f899904dc68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48979.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48979
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
