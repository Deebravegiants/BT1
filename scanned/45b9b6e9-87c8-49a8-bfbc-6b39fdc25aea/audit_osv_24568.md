# [H] CVE-2023-22995

## Summary
Severity: High
Advisory: CVE-2023-22995
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-22995
Type: osv

## Details
In the Linux kernel before 5.17, an error path in dwc3_qcom_acpi_register_core in drivers/usb/dwc3/dwc3-qcom.c lacks certain platform_device_put and kfree calls.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22995.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22995
- https://security.netapp.com/advisory/ntap-20230331-0004/
- https://github.com/torvalds/linux/commit/fa0ef93868a6062babe1144df2807a8b1d4924d2
