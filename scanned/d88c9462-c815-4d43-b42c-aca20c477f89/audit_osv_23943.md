# [M] usb: gadget: lpc32xx_udc: Fix refcount leak in lpc32xx_udc_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49712
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49712
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <4.9.320, >=4.10.0 <4.14.285, >=4.15.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: lpc32xx_udc: Fix refcount leak in lpc32xx_udc_probe

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.
of_node_put() will check NULL pointer.

## References
- https://git.kernel.org/stable/c/0ef6917c0524da5b88496b9706628ffef108b9bb
- https://git.kernel.org/stable/c/2a598da14856ead80c726b38ba426c68637d9211
- https://git.kernel.org/stable/c/46da1e4a8b6329479433b2a4056941dfdd7f3efd
- https://git.kernel.org/stable/c/4757c9ade34178b351580133771f510b5ffcf9c8
- https://git.kernel.org/stable/c/57901c658f77d9ea2e772f35cb38e47efb54c558
- https://git.kernel.org/stable/c/727c82d003e0ec64411fd1257a9a57de4ad7a99a
- https://git.kernel.org/stable/c/b75bddfcc18170ce8e3fb695a76ec2dec4ce0ea5
- https://git.kernel.org/stable/c/d85e4e6284a91aa2d1ab004e9d84b9c09b4aa203
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49712.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49712
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
