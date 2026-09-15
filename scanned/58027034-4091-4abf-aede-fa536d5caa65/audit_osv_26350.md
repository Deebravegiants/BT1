# [H] drm/amdgpu: fix possible UAF in amdgpu_cs_pass1()

## Summary
Severity: High
Advisory: CVE-2023-52921
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2023-52921
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix possible UAF in amdgpu_cs_pass1()

Since the gang_size check is outside of chunk parsing
loop, we need to reset i before we free the chunk data.

Suggested by Ye Zhang (@VAR10CK) of Baidu Security.

## References
- https://git.kernel.org/stable/c/90e065677e0362a777b9db97ea21d43a39211399
- https://git.kernel.org/stable/c/e08e9dd09809b16f8f8cee8c466841b33d24ed96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52921.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52921
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
