# [M] kunit: Fix potential null dereference in kunit_device_driver_test()

## Summary
Severity: Medium
Advisory: CVE-2024-56773
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56773
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

kunit: Fix potential null dereference in kunit_device_driver_test()

kunit_kzalloc() may return a NULL pointer, dereferencing it without
NULL check may lead to NULL dereference.
Add a NULL check for test_state.

## References
- https://git.kernel.org/stable/c/435c20eed572a95709b1536ff78832836b2f91b1
- https://git.kernel.org/stable/c/5d28fac59369b5d3c48cdf09e50275a61ff91202
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56773.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56773
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
