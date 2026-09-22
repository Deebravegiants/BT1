# [H] media: uvcvideo: Fix crash during unbind if gpio unit is in use

## Summary
Severity: High
Advisory: CVE-2024-58079
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58079
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: uvcvideo: Fix crash during unbind if gpio unit is in use

We used the wrong device for the device managed functions. We used the
usb device, when we should be using the interface device.

If we unbind the driver from the usb interface, the cleanup functions
are never called. In our case, the IRQ is never disabled.

If an IRQ is triggered, it will try to access memory sections that are
already free, causing an OOPS.

We cannot use the function devm_request_threaded_irq here. The devm_*
clean functions may be called after the main structure is released by
uvc_delete.

Luckily this bug has small impact, as it is only affected by devices
with gpio units and the user has to unbind the device, a disconnect will
not trigger this error.

## References
- https://git.kernel.org/stable/c/0b5e0445bc8384c18bd35cb9fe87f6258c6271d9
- https://git.kernel.org/stable/c/0fdd7cc593385e46e92e180b71e264fc9c195298
- https://git.kernel.org/stable/c/3c00e94d00ca079bef7906d6f39d1091bccfedd3
- https://git.kernel.org/stable/c/5d2e65cbe53d0141ed095cf31c2dcf3d8668c11d
- https://git.kernel.org/stable/c/a9ea1a3d88b7947ce8cadb2afceee7a54872bbc5
- https://git.kernel.org/stable/c/d2eac8b14ac690aa73052aa6d4ba69005715367e
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58079.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58079
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
