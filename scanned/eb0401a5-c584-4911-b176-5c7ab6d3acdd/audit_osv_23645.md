# [M] coresight: syscfg: Fix memleak on registration failure in cscfg_create_device

## Summary
Severity: Medium
Advisory: CVE-2022-49284
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49284
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

coresight: syscfg: Fix memleak on registration failure in cscfg_create_device

device_register() calls device_initialize(),
according to doc of device_initialize:

    Use put_device() to give up your reference instead of freeing
    * @dev directly once you have called this function.

To prevent potential memleak, use put_device() for error handling.

## References
- https://git.kernel.org/stable/c/412225b32986d5b11c3c1ad9234c50a3f5c52c76
- https://git.kernel.org/stable/c/a529af1f5a5c096f3e18f0d5a32cfcc3d82df1ec
- https://git.kernel.org/stable/c/c61e2fc87f24cae4701f352fe9ecd4c5c143106c
- https://git.kernel.org/stable/c/cfa5dbcdd7aece76f3415284569f2f384aff0253
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49284.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
