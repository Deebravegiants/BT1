# [H] driver core: fix potential NULL pointer dereference in dev_uevent()

## Summary
Severity: High
Advisory: CVE-2025-37800
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-37800
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

driver core: fix potential NULL pointer dereference in dev_uevent()

If userspace reads "uevent" device attribute at the same time as another
threads unbinds the device from its driver, change to dev->driver from a
valid pointer to NULL may result in crash. Fix this by using READ_ONCE()
when fetching the pointer, and take bus' drivers klist lock to make sure
driver instance will not disappear while we access it.

Use WRITE_ONCE() when setting the driver pointer to ensure there is no
tearing.

## References
- https://git.kernel.org/stable/c/18daa52418e7e4629ed1703b64777294209d2622
- https://git.kernel.org/stable/c/2b344e779d9afd0fcb5ee4000e4d0fc7d8d867eb
- https://git.kernel.org/stable/c/3781e4b83e174364998855de777e184cf0b62c40
- https://git.kernel.org/stable/c/abe56be73eb10a677d16066f65ff9d30251f5eee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37800.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37800
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
