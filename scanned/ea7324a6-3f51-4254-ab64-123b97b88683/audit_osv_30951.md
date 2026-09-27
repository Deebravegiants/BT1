# [M] ACPI: x86: Add adev NULL check to acpi_quirk_skip_serdev_enumeration()

## Summary
Severity: Medium
Advisory: CVE-2024-56782
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56782
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: x86: Add adev NULL check to acpi_quirk_skip_serdev_enumeration()

acpi_dev_hid_match() does not check for adev == NULL, dereferencing
it unconditional.

Add a check for adev being NULL before calling acpi_dev_hid_match().

At the moment acpi_quirk_skip_serdev_enumeration() is never called with
a controller_parent without an ACPI companion, but better safe than sorry.

## References
- https://git.kernel.org/stable/c/4a49194f587a62d972b602e3e1a2c3cfe6567966
- https://git.kernel.org/stable/c/e173bce05f7032a8b4964cfef82a4b7668f5f3af
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56782.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56782
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
