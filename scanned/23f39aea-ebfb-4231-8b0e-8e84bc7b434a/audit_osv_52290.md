# [M] CVE-2021-47289

## Summary
Severity: Medium
Advisory: CVE-2021-47289
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47289
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: fix NULL pointer dereference

Commit 71f642833284 ("ACPI: utils: Fix reference counting in
for_each_acpi_dev_match()") started doing "acpi_dev_put()" on a pointer
that was possibly NULL.  That fails miserably, because that helper
inline function is not set up to handle that case.

Just make acpi_dev_put() silently accept a NULL pointer, rather than
calling down to put_device() with an invalid offset off that NULL
pointer.

## References
- https://git.kernel.org/stable/c/38f54217b423c0101d03a00feec6fb8ec608b12e
- https://git.kernel.org/stable/c/cae3fa3d8165761f3000f523b11cfa1cd35206bc
- https://git.kernel.org/stable/c/ccf23a0888077a25a0793a746c3941db2a7562e4
- https://git.kernel.org/stable/c/fc68f42aa737dc15e7665a4101d4168aadb8e4c4
