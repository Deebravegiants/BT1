# [H] driver: base: fix UAF when driver_attach failed

## Summary
Severity: High
Advisory: CVE-2022-49385
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49385
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

driver: base: fix UAF when driver_attach failed

When driver_attach(drv); failed, the driver_private will be freed.
But it has been added to the bus, which caused a UAF.

To fix it, we need to delete it from the bus when failed.

## References
- https://git.kernel.org/stable/c/310862e574001a97ad02272bac0fd13f75f42a27
- https://git.kernel.org/stable/c/5389101257828d1913d713d9a40acbe14f5961df
- https://git.kernel.org/stable/c/5d709f58c743166fe1c6914b9de0ae8868600d9b
- https://git.kernel.org/stable/c/823f24f2e329babd0330200d0b74882516fe57f4
- https://git.kernel.org/stable/c/c059665c84feab46b7173d3a1bf36c2fb7f9df86
- https://git.kernel.org/stable/c/cdf1a683a01583bca4b618dd16223cbd6e462e21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49385.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49385
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
