# [M] firewire: test: Fix potential null dereference in firewire kunit test

## Summary
Severity: Medium
Advisory: CVE-2025-21798
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21798
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

firewire: test: Fix potential null dereference in firewire kunit test

kunit_kzalloc() may return a NULL pointer, dereferencing it without
NULL check may lead to NULL dereference.
Add a NULL check for test_state.

## References
- https://git.kernel.org/stable/c/352fafe97784e81a10a7c74bd508f71a19b53c2a
- https://git.kernel.org/stable/c/70fcb25472d90dd3b87cbee74b9eb68670b0c7b8
- https://git.kernel.org/stable/c/c6896bf4c611c3dd126f3e03685f2360a18b3d6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21798.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21798
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
