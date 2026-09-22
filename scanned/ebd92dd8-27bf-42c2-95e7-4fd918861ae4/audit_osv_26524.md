# [H] net: fec: Better handle pm_runtime_get() failing in .remove()

## Summary
Severity: High
Advisory: CVE-2023-53308
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53308
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.4.0 <5.10.181, >=5.5.0 <5.15.113, >=5.11.0 <6.1.30, >=5.16.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fec: Better handle pm_runtime_get() failing in .remove()

In the (unlikely) event that pm_runtime_get() (disguised as
pm_runtime_resume_and_get()) fails, the remove callback returned an
error early. The problem with this is that the driver core ignores the
error value and continues removing the device. This results in a
resource leak. Worse the devm allocated resources are freed and so if a
callback of the driver is called later the register mapping is already
gone which probably results in a crash.

## References
- https://git.kernel.org/stable/c/83996d317b1deddc85006376082e8886f55aa709
- https://git.kernel.org/stable/c/9407454a9b18bbeff216e8ecde87ffb2171e9ccf
- https://git.kernel.org/stable/c/b22b514209ff8c4287abb853399890ab97e1b5ca
- https://git.kernel.org/stable/c/be85912c36ddca3e8b2eef1b5392cd8db6bdb730
- https://git.kernel.org/stable/c/c1bc2870f14e526a01897e14c747a0a0ca125231
- https://git.kernel.org/stable/c/d52a0cca591e899d4e5c8ab19e067b4c6b7d104f
- https://git.kernel.org/stable/c/e02d8d5b1602689b98d9b91550a11b9b57baedbe
- https://git.kernel.org/stable/c/f816b9829b19394d318e01953aa3b2721bca040d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53308.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53308
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
