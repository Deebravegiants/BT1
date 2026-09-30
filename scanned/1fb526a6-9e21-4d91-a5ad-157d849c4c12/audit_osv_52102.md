# [M] CVE-2021-47073

## Summary
Severity: Medium
Advisory: CVE-2021-47073
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-01
Source: https://osv.dev/vulnerability/CVE-2021-47073
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: dell-smbios-wmi: Fix oops on rmmod dell_smbios

init_dell_smbios_wmi() only registers the dell_smbios_wmi_driver on systems
where the Dell WMI interface is supported. While exit_dell_smbios_wmi()
unregisters it unconditionally, this leads to the following oops:

[  175.722921] ------------[ cut here ]------------
[  175.722925] Unexpected driver unregister!
[  175.722939] WARNING: CPU: 1 PID: 3630 at drivers/base/driver.c:194 driver_unregister+0x38/0x40
...
[  175.723089] Call Trace:
[  175.723094]  cleanup_module+0x5/0xedd [dell_smbios]
...
[  175.723148] ---[ end trace 064c34e1ad49509d ]---

Make the unregister happen on the same condition the register happens
to fix this.

## References
- https://git.kernel.org/stable/c/0cf036a0d325200e6c27b90908e51195bbc557b1
- https://git.kernel.org/stable/c/3a53587423d25c87af4b4126a806a0575104b45e
- https://git.kernel.org/stable/c/6fa78a6b9a3beb676a010dc489c1257f7e432525
- https://git.kernel.org/stable/c/75cfc833da4a2111106d4c134e93e0c7f41e35e7
- https://git.kernel.org/stable/c/8d746ea7c687bab060a2c05a35c449302406cd52
