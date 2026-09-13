# [H] misc: ocxl: fix possible double free in ocxl_file_register_afu

## Summary
Severity: High
Advisory: CVE-2022-49455
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49455
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: ocxl: fix possible double free in ocxl_file_register_afu

info_release() will be called in device_unregister() when info->dev's
reference count is 0. So there is no need to call ocxl_afu_put() and
kfree() again.

Fix this by adding free_minor() and return to err_unregister error path.

## References
- https://git.kernel.org/stable/c/252768d32e92c1214aeebb5fec0844ca479bcf5c
- https://git.kernel.org/stable/c/8fb674216835e1f0c143762696d645facebb4685
- https://git.kernel.org/stable/c/950cf957fe34d40d63dfa3bf3968210430b6491e
- https://git.kernel.org/stable/c/9e9087cf34ee69f4e95d146ac29385d6e367a97b
- https://git.kernel.org/stable/c/de65c32ace9aa70d51facc61ba986607075e3a25
- https://git.kernel.org/stable/c/ee89d8dee55ab4b3b8ad8b70866b2841ba334767
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49455.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49455
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
