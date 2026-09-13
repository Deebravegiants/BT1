# [H] eeprom: at24: fix memory corruption race condition

## Summary
Severity: High
Advisory: CVE-2024-35848
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35848
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

eeprom: at24: fix memory corruption race condition

If the eeprom is not accessible, an nvmem device will be registered, the
read will fail, and the device will be torn down. If another driver
accesses the nvmem device after the teardown, it will reference
invalid memory.

Move the failure point before registering the nvmem device.

## References
- https://git.kernel.org/stable/c/26d32bec4c6d255a03762f33c637bfa3718be15a
- https://git.kernel.org/stable/c/2af84c46b9b8f2d6c0f88d09ee5c849ae1734676
- https://git.kernel.org/stable/c/6d8b56ec0c8f30d5657382f47344a32569f7a9bc
- https://git.kernel.org/stable/c/c43e5028f5a35331eb25017f5ff6cc21735005c6
- https://git.kernel.org/stable/c/c850f71fca09ea41800ed55905980063d17e01da
- https://git.kernel.org/stable/c/f42c97027fb75776e2e9358d16bf4a99aeb04cf2
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35848.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35848
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
