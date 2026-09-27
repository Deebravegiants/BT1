# [H] drm/amdgpu: fix mmhub client id out-of-bounds access

## Summary
Severity: High
Advisory: CVE-2024-27029
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27029
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix mmhub client id out-of-bounds access

Properly handle cid 0x140.

## References
- https://git.kernel.org/stable/c/1f24b3040f2b6ffcb97151fabb3070328254d923
- https://git.kernel.org/stable/c/6540ff6482c1a5a6890ae44b23d0852ba1986d9e
- https://git.kernel.org/stable/c/e1e076bda4fd6378ae650f2c6ef1a4ff93c5aea5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27029.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27029
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
