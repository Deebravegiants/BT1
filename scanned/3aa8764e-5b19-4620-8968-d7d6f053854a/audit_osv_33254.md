# [H] gpiolib: acpi: initialize acpi_gpio_info struct

## Summary
Severity: High
Advisory: CVE-2025-39960
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-39960
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpiolib: acpi: initialize acpi_gpio_info struct

Since commit 7c010d463372 ("gpiolib: acpi: Make sure we fill struct
acpi_gpio_info"), uninitialized acpi_gpio_info struct are passed to
__acpi_find_gpio() and later in the call stack info->quirks is used in
acpi_populate_gpio_lookup. This breaks the i2c_hid_cpi driver:

[   58.122916] i2c_hid_acpi i2c-UNIW0001:00: HID over i2c has not been provided an Int IRQ
[   58.123097] i2c_hid_acpi i2c-UNIW0001:00: probe with driver i2c_hid_acpi failed with error -22

Fix this by initializing the acpi_gpio_info pass to __acpi_find_gpio()

## References
- https://git.kernel.org/stable/c/19c839a98c731169f06d32e7c9e00c78a0086ebe
- https://git.kernel.org/stable/c/27d94a2a52cbb54927c0140bd5b978c56e9a283a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39960.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39960
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
