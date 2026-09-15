# [H] driver core: bus: Fix double free in driver API bus_register()

## Summary
Severity: High
Advisory: CVE-2024-50055
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50055
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

driver core: bus: Fix double free in driver API bus_register()

For bus_register(), any error which happens after kset_register() will
cause that @priv are freed twice, fixed by setting @priv with NULL after
the first free.

## References
- https://git.kernel.org/stable/c/9ce15f68abedfae7ae0a35e95895aeddfd0f0c6a
- https://git.kernel.org/stable/c/bfa54a793ba77ef696755b66f3ac4ed00c7d1248
- https://git.kernel.org/stable/c/d885c464c25018b81a6b58f5d548fc2e3ef87dd1
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50055.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50055
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
