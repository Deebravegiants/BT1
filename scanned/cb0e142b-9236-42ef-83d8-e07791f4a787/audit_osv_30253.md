# [M] phy: qcom: qmp-usbc: fix NULL-deref on runtime suspend

## Summary
Severity: Medium
Advisory: CVE-2024-50238
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50238
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: qcom: qmp-usbc: fix NULL-deref on runtime suspend

Commit 413db06c05e7 ("phy: qcom-qmp-usb: clean up probe initialisation")
removed most users of the platform device driver data from the
qcom-qmp-usb driver, but mistakenly also removed the initialisation
despite the data still being used in the runtime PM callbacks. This bug
was later reproduced when the driver was copied to create the qmp-usbc
driver.

Restore the driver data initialisation at probe to avoid a NULL-pointer
dereference on runtime suspend.

Apparently no one uses runtime PM, which currently needs to be enabled
manually through sysfs, with these drivers.

## References
- https://git.kernel.org/stable/c/34c21f94fa1e147a19b54b6adf0c93a623b70dd8
- https://git.kernel.org/stable/c/c7086dc0539b1b2b61c8c735186698bca4858246
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50238.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50238
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
