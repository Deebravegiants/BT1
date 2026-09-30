# [M] CVE-2021-47425

## Summary
Severity: Medium
Advisory: CVE-2021-47425
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47425
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: acpi: fix resource leak in reconfiguration device addition

acpi_i2c_find_adapter_by_handle() calls bus_find_device() which takes a
reference on the adapter which is never released which will result in a
reference count leak and render the adapter unremovable.  Make sure to
put the adapter after creating the client in the same manner that we do
for OF.

[wsa: fixed title]

## References
- https://git.kernel.org/stable/c/3d9d458a8aaafa47268ea4f1b4114a9f12927989
- https://git.kernel.org/stable/c/60bacf259e8c2eb2324f3e13275200baaee9494b
- https://git.kernel.org/stable/c/6558b646ce1c2a872fe1c2c7cb116f05a2c1950f
- https://git.kernel.org/stable/c/90f1077c9184ec2ae9989e4642f211263f301694
- https://git.kernel.org/stable/c/b8090a84d7758b929d348bafbd86bb7a10c5fb63
- https://git.kernel.org/stable/c/f86de018fd7a24ee07372d55ffa7824f0c674a95
