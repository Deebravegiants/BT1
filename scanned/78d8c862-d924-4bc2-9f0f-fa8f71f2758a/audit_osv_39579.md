# [H] drm/amdgpu/vcn4: Prevent OOB reads when parsing dec msg

## Summary
Severity: High
Advisory: CVE-2026-46199
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46199
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/vcn4: Prevent OOB reads when parsing dec msg

Check bounds against the end of the BO whenever we access the msg.

## References
- https://git.kernel.org/stable/c/0a78f2bac1424deb7c9d5e09c6b8e849d8e8b648
- https://git.kernel.org/stable/c/3c817a60b09eaab926e475088e750936efcc95ae
- https://git.kernel.org/stable/c/63b51e8a9d54317d31cc3856c1e12407070d5fc2
- https://git.kernel.org/stable/c/7688143ca62edeecacb3ba0a2cea129dbd262a18
- https://git.kernel.org/stable/c/88411caee8f576d6b5abf6531232fcc0ce756dc5
- https://git.kernel.org/stable/c/c72a8b4dc6d598e3831ef3abd9c6527dfbf4810e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46199.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46199
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
