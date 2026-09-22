# [M] char: xillybus: fix a refcount leak in cleanup_dev()

## Summary
Severity: Medium
Advisory: CVE-2022-49310
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49310
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

char: xillybus: fix a refcount leak in cleanup_dev()

usb_get_dev is called in xillyusb_probe. So it is better to call
usb_put_dev before xdev is released.

## References
- https://git.kernel.org/stable/c/21f1f167d727f3f857e26d509ef5a6d47fd31bc3
- https://git.kernel.org/stable/c/b67d19662fdee275c479d21853bc1239600a798f
- https://git.kernel.org/stable/c/bc8fceda3b89006e8a7dda8a097d36045d044c25
- https://git.kernel.org/stable/c/e277b95acdab84cd5d2f8d537a37aef6d21e988b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49310.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49310
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
