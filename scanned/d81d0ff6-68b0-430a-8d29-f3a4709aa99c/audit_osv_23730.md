# [M] lib/string_helpers: fix not adding strarray to device's resource list

## Summary
Severity: Medium
Advisory: CVE-2022-49403
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49403
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

lib/string_helpers: fix not adding strarray to device's resource list

Add allocated strarray to device's resource list. This is a must to
automatically release strarray when the device disappears.

Without this fix we have a memory leak in the few drivers which use
devm_kasprintf_strarray().

## References
- https://git.kernel.org/stable/c/a152eb42fcecfe41239c3c6695342f3a128593e7
- https://git.kernel.org/stable/c/bf29edab0c9ff3d2633b8306a67d04c357e2a385
- https://git.kernel.org/stable/c/cd290a9839cee2f6641558877e707bd373c8f6f1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49403.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49403
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
