# [H] Revert "usb: typec: ucsi: add a common function ucsi_unregister_connectors()"

## Summary
Severity: High
Advisory: CVE-2022-49944
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49944
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "usb: typec: ucsi: add a common function ucsi_unregister_connectors()"

The recent commit 87d0e2f41b8c ("usb: typec: ucsi: add a common
function ucsi_unregister_connectors()") introduced a regression that
caused NULL dereference at reading the power supply sysfs.  It's a
stale sysfs entry that should have been removed but remains with NULL
ops.  The commit changed the error handling to skip the entries after
a NULL con->wq, and this leaves the power device unreleased.

For addressing the regression, the straight revert is applied here.
Further code improvements can be done from the scratch again.

## References
- https://git.kernel.org/stable/c/3d4044c9e6d2e3f11f1f8b5e0ee8647d3eb1afad
- https://git.kernel.org/stable/c/5f73aa2cf8bef4a39baa1591c3144ede4788826e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49944.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49944
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
