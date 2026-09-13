# [M] CVE-2023-22999

## Summary
Severity: Medium
Advisory: CVE-2023-22999
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-22999
Type: osv

## Details
In the Linux kernel before 5.16.3, drivers/usb/dwc3/dwc3-qcom.c misinterprets the dwc3_qcom_create_urs_usb_platdev return value (expects it to be NULL in the error case, whereas it is actually an error pointer).

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.3
- https://github.com/torvalds/linux/commit/b52fe2dbb3e655eb1483000adfab68a219549e13
