# [M] HID: sony: Fix a potential memory leak in sony_probe()

## Summary
Severity: Medium
Advisory: CVE-2023-52529
Ecosystem: Linux
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52529
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.135, >=5.16.0 <6.1.57, >=6.2.0 <6.5.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: sony: Fix a potential memory leak in sony_probe()

If an error occurs after a successful usb_alloc_urb() call, usb_free_urb()
should be called.

## References
- https://git.kernel.org/stable/c/bb0707fde7492121917fd9ddb43829e96ec0bb9e
- https://git.kernel.org/stable/c/e1cd4004cde7c9b694bbdd8def0e02288ee58c74
- https://git.kernel.org/stable/c/f237b17611fa3501f43f12d1cb64323e10fdcb4f
- https://git.kernel.org/stable/c/f566efa7de1e35e6523f4acbaf85068a540be07d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52529.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52529
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
