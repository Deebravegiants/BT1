# [H] platform/x86: x86-android-tablets: Fix use after free on platform_device_register() errors

## Summary
Severity: High
Advisory: CVE-2024-49986
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49986
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.118, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: x86-android-tablets: Fix use after free on platform_device_register() errors

x86_android_tablet_remove() frees the pdevs[] array, so it should not
be used after calling x86_android_tablet_remove().

When platform_device_register() fails, store the pdevs[x] PTR_ERR() value
into the local ret variable before calling x86_android_tablet_remove()
to avoid using pdevs[] after it has been freed.

## References
- https://git.kernel.org/stable/c/2fae3129c0c08e72b1fe93e61fd8fd203252094a
- https://git.kernel.org/stable/c/73a98cf79e4dbfa3d0c363e826c65aae089b313c
- https://git.kernel.org/stable/c/aac871e493fc8809e60209d9899b1af07e9dbfc8
- https://git.kernel.org/stable/c/ba0b09a2f327319e252d8f3032019b958c0a5cd9
- https://git.kernel.org/stable/c/f08adc5177bd4343df09033f62ab562c09ba7f7d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49986.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49986
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
