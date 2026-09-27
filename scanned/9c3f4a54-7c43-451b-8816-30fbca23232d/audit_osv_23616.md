# [M] power: supply: ab8500: Fix memory leak in ab8500_fg_sysfs_init

## Summary
Severity: Medium
Advisory: CVE-2022-49224
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49224
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

power: supply: ab8500: Fix memory leak in ab8500_fg_sysfs_init

kobject_init_and_add() takes reference even when it fails.
According to the doc of kobject_init_and_add()：

   If this function returns an error, kobject_put() must be called to
   properly clean up the memory associated with the object.

Fix memory leak by calling kobject_put().

## References
- https://git.kernel.org/stable/c/19aa3c98ed7b2616e105946cec804f897837ab84
- https://git.kernel.org/stable/c/261041097ab3470f1120b7733cbf472712304d1e
- https://git.kernel.org/stable/c/31cdf7897dba1f096b74f69d840f0575b8cdb9ae
- https://git.kernel.org/stable/c/41ed61364285ff38bbbe9ca8a45c8372ba72921d
- https://git.kernel.org/stable/c/6a4760463dbc6b603690938c468839985189ce0a
- https://git.kernel.org/stable/c/879356a6a05559582b0a7895d86d2d4359745c08
- https://git.kernel.org/stable/c/c32f6b6196b6efc1c68990dfeaac36fb8eb3b8e1
- https://git.kernel.org/stable/c/db3a61ef8e6aef3b888baa6a85926c2230c2cc56
- https://git.kernel.org/stable/c/ffb8e92b4cef92bd25563cf3d8b4489eb22bc61f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49224.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49224
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
