# [M] usb: phy: phy-tahvo: fix memory leak in tahvo_usb_probe()

## Summary
Severity: Medium
Advisory: CVE-2023-53379
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53379
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.15.0 <6.1.39, >=5.16.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: phy: phy-tahvo: fix memory leak in tahvo_usb_probe()

Smatch reports:
drivers/usb/phy/phy-tahvo.c: tahvo_usb_probe()
warn: missing unwind goto?

After geting irq, if ret < 0, it will return without error handling to
free memory.
Just add error handling to fix this problem.

## References
- https://git.kernel.org/stable/c/342161c11403ea00e9febc16baab1d883d589d04
- https://git.kernel.org/stable/c/38dbd6f72bfbeba009efe0e9ec1f3ff09f9e23fa
- https://git.kernel.org/stable/c/3e5a7bebf832b1482efe27bcc15a88c5b28a30d0
- https://git.kernel.org/stable/c/4da9edeccf77d7b4c6dbcb34d5908acdaa5bd7e3
- https://git.kernel.org/stable/c/56901de563359de20513e16a9ae008ae2c22e9a9
- https://git.kernel.org/stable/c/dd9b7c89a80428cc5f4ae0d2e1311fdedb2a1aac
- https://git.kernel.org/stable/c/ecf26d6e1b5450620c214feea537bb6ce05c6741
- https://git.kernel.org/stable/c/fe9cdc19861950582f077f254a12026e169eaee5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53379.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53379
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
