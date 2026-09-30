# [M] usb: dwc2: Fix memory leak in dwc2_hcd_init

## Summary
Severity: Medium
Advisory: CVE-2022-49713
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49713
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.285, >=4.15.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.15.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc2: Fix memory leak in dwc2_hcd_init

usb_create_hcd will alloc memory for hcd, and we should
call usb_put_hcd to free it when platform_get_resource()
fails to prevent memory leak.
goto error2 label instead error1 to fix this.

## References
- https://git.kernel.org/stable/c/3755278f078460b021cd0384562977bf2039a57a
- https://git.kernel.org/stable/c/52bfcedbfd5bf962dbdcb6e761f4d0dd3ba26dfd
- https://git.kernel.org/stable/c/6506aff2dc2f7059aa3d45ee2e8639b25e87090f
- https://git.kernel.org/stable/c/701d8ec01e0f229d4db6f43d3d64ee479120cbeb
- https://git.kernel.org/stable/c/84e6d0af87e27bbc0db94f2e7323b34abe17b6e5
- https://git.kernel.org/stable/c/981ee40649e5fd9550f82db1fbb3bfab037da346
- https://git.kernel.org/stable/c/a44a8a762f7fe9ad3c065813d058e835a6180cb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49713.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49713
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
