# [M] drm/amd/display: Initialize denominator defaults to 1

## Summary
Severity: Medium
Advisory: CVE-2024-57950
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-10
Source: https://osv.dev/vulnerability/CVE-2024-57950
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Initialize denominator defaults to 1

[WHAT & HOW]
Variables, used as denominators and maybe not assigned to other values,
should be initialized to non-zero to avoid DIVIDE_BY_ZERO, as reported
by Coverity.

(cherry picked from commit e2c4c6c10542ccfe4a0830bb6c9fd5b177b7bbb7)

## References
- https://git.kernel.org/stable/c/36b23e3baf9129d5b6c3a3a85b6b7ffb75ae287c
- https://git.kernel.org/stable/c/c9d6afb4f9c338049662d27d169fba7dd60e337d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57950.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57950
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
