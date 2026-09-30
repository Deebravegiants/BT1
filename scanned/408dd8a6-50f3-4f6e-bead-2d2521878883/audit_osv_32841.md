# [H] net/mdiobus: Fix potential out-of-bounds clause 45 read/write access

## Summary
Severity: High
Advisory: CVE-2025-38110
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38110
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mdiobus: Fix potential out-of-bounds clause 45 read/write access

When using publicly available tools like 'mdio-tools' to read/write data
from/to network interface and its PHY via C45 (clause 45) mdiobus,
there is no verification of parameters passed to the ioctl and
it accepts any mdio address.
Currently there is support for 32 addresses in kernel via PHY_MAX_ADDR define,
but it is possible to pass higher value than that via ioctl.
While read/write operation should generally fail in this case,
mdiobus provides stats array, where wrong address may allow out-of-bounds
read/write.

Fix that by adding address verification before C45 read/write operation.
While this excludes this access from any statistics, it improves security of
read/write operation.

## References
- https://git.kernel.org/stable/c/260388f79e94fb3026c419a208ece8358bb7b555
- https://git.kernel.org/stable/c/31bf7b2b92563a352788cf9df3698682f659bacc
- https://git.kernel.org/stable/c/4ded22f7f3ce9714ed72c3e9c68fea1cb9388ae7
- https://git.kernel.org/stable/c/abb0605ca00979a49572a6516f6db22c3dc57223
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38110.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38110
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
