# [H] ACPI: sysfs: validate return type of _STR method

## Summary
Severity: High
Advisory: CVE-2024-49860
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49860
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: sysfs: validate return type of _STR method

Only buffer objects are valid return values of _STR.

If something else is returned description_show() will access invalid
memory.

## References
- https://git.kernel.org/stable/c/0cdfb9178a3bba843c95c2117c82c15f1a64b9ce
- https://git.kernel.org/stable/c/2364b6af90c6b6d8a4783e0d3481ca80af699554
- https://git.kernel.org/stable/c/4b081991c4363e072e1748efed0bbec8a77daba5
- https://git.kernel.org/stable/c/4bb1e7d027413835b086aed35bc3f0713bc0f72b
- https://git.kernel.org/stable/c/5c8d007c14aefc3f2ddf71e4c40713733dc827be
- https://git.kernel.org/stable/c/92fd5209fc014405f63a7db79802ca4b01dc0c05
- https://git.kernel.org/stable/c/f0921ecd4ddc14646bb5511f49db4d7d3b0829f0
- https://git.kernel.org/stable/c/f51e5a88f2e7224858b261546cf6b3037dfb1323
- https://git.kernel.org/stable/c/f51f711d36e61fbb87c67b524fd200e05172668d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49860.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49860
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
