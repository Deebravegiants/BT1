# [M] CVE-2020-11933

## Summary
Severity: Medium
Advisory: CVE-2020-11933
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/CVE-2020-11933
Type: osv

## Details
cloud-init as managed by snapd on Ubuntu Core 16 and Ubuntu Core 18 devices was run without restrictions on every boot, which a physical attacker could exploit by crafting cloud-init user-data/meta-data via external media to perform arbitrary changes on the device to bypass intended security mechanisms such as full disk encryption. This issue did not affect traditional Ubuntu systems. Fixed in snapd version 2.45.2, revision 8539 and core version 2.45.2, revision 9659.

## References
- https://launchpad.net/bugs/1879530
- https://ubuntu.com/USN-4424-1
