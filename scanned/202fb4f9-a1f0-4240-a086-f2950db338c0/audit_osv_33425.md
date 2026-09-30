# [H] drm/amdgpu: validate userq buffer virtual address and size

## Summary
Severity: High
Advisory: CVE-2025-40334
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-40334
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: validate userq buffer virtual address and size

It needs to validate the userq object virtual address to
determine whether it is residented in a valid vm mapping.

## References
- https://git.kernel.org/stable/c/5a577de86c4a1c67ca405571d6ef84e65c6897d1
- https://git.kernel.org/stable/c/9e46b8bb0539d7bc9a9e7b3072fa4f6082490392
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40334.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40334
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
