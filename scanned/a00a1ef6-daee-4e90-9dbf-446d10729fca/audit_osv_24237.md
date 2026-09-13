# [H] platform/chrome: fix memory corruption in ioctl

## Summary
Severity: High
Advisory: CVE-2022-50570
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2022-50570
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/chrome: fix memory corruption in ioctl

If "s_mem.bytes" is larger than the buffer size it leads to memory
corruption.

## References
- https://git.kernel.org/stable/c/0c2e18924504208644d18415667895a4ac54cf2a
- https://git.kernel.org/stable/c/868fc93b615b9f6c2b0b1894536618fa6cd66acc
- https://git.kernel.org/stable/c/8a07b45fd3c2dda24fad43639be5335a4595196a
- https://git.kernel.org/stable/c/e548f9503c4b3292a60a63fe77dccea62999a35a
- https://git.kernel.org/stable/c/f143f1d9a8e5c6c9db3de81ca270191226fcce36
- https://git.kernel.org/stable/c/fd1d3b265784a2243fcaef06aebfb2f8ee733cec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50570.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
