# [H] kunit/overflow: Fix UB in overflow_allocation_test

## Summary
Severity: High
Advisory: CVE-2024-46823
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46823
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

kunit/overflow: Fix UB in overflow_allocation_test

The 'device_name' array doesn't exist out of the
'overflow_allocation_test' function scope. However, it is being used as
a driver name when calling 'kunit_driver_create' from
'kunit_device_register'. It produces the kernel panic with KASAN
enabled.

Since this variable is used in one place only, remove it and pass the
device name into kunit_device_register directly as an ascii string.

## References
- https://git.kernel.org/stable/c/92e9bac18124682c4b99ede9ee3bcdd68f121e92
- https://git.kernel.org/stable/c/d1207f07decc66546a7fa463d2f335a856c986ef
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46823.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46823
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
