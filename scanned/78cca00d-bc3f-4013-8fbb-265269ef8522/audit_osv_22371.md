# [H] CVE-2022-27223

## Summary
Severity: High
Advisory: CVE-2022-27223
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2022-27223
Type: osv

## Details
In drivers/usb/gadget/udc/udc-xilinx.c in the Linux kernel before 5.16.12, the endpoint index is not validated and might be manipulated by the host for out-of-array access.

## References
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://security.netapp.com/advisory/ntap-20220419-0001/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.12
- https://github.com/torvalds/linux/commit/7f14c7227f342d9932f9b918893c8814f86d2a0d
