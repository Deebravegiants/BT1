# [M] drm/amd/display: Fix a debugfs null pointer error

## Summary
Severity: Medium
Advisory: CVE-2023-52673
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52673
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix a debugfs null pointer error

[WHY & HOW]
Check whether get_subvp_en() callback exists before calling it.

## References
- https://git.kernel.org/stable/c/43235db21fc23559f50a62f8f273002eeb506f5a
- https://git.kernel.org/stable/c/efb91fea652a42fcc037d2a9ef4ecd1ffc5ff4b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52673.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52673
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
