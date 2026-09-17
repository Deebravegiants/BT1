# [M] mctp: Fix an error handling path in mctp_init()

## Summary
Severity: Medium
Advisory: CVE-2022-49854
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49854
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mctp: Fix an error handling path in mctp_init()

If mctp_neigh_init() return error, the routes resources should
be released in the error handling path. Otherwise some resources
leak.

## References
- https://git.kernel.org/stable/c/216c83222d2eb24b0e63df56e8740b02c33286e8
- https://git.kernel.org/stable/c/49d8a6e24a3496d86e8d8ae748375df984fb6d6f
- https://git.kernel.org/stable/c/d4072058af4fd8fb4658e7452289042a406a9398
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49854.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49854
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
