# [M] drm/amd/display: Fix memory leak

## Summary
Severity: Medium
Advisory: CVE-2022-49135
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49135
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.258, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix memory leak

[why]
Resource release is needed on the error handling path
to prevent memory leak.

[how]
Fix this by adding kfree on the error handling path.

## References
- https://git.kernel.org/stable/c/3ce1497add6d17b48cc9df65095bd20202d93994
- https://git.kernel.org/stable/c/5076315aaddd640bde896ec8d79423ed8ec83a59
- https://git.kernel.org/stable/c/5d5c6dba2b43e28845d7d7ed32a36802329a5f52
- https://git.kernel.org/stable/c/7e10369c72db7a0e2f77b2e306aadc07aef6b07a
- https://git.kernel.org/stable/c/9d0bef3cc22cf250278ed45b829f062a00af9e27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49135.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49135
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
