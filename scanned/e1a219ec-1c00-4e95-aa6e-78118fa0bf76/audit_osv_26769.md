# [H] drm/ttm: Don't leak a resource on swapout move error

## Summary
Severity: High
Advisory: CVE-2023-53844
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53844
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/ttm: Don't leak a resource on swapout move error

If moving the bo to system for swapout failed, we were leaking
a resource. Fix.

## References
- https://git.kernel.org/stable/c/4a5b37ea6797d7a53e6dd004aa37e149f40199ce
- https://git.kernel.org/stable/c/a590f03d8de7c4cb7ce4916dc7f2fd10711faabe
- https://git.kernel.org/stable/c/af4e0ce2af8a8f0ff3b89702a1e18d8ec2c4a834
- https://git.kernel.org/stable/c/f037f6038736bd038ddb9c72de979a08cc1ee3b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53844.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53844
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
