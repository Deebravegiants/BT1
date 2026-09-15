# [H] USBX Host CDC ECM integer underflow with buffer overflow

## Summary
Severity: High
Advisory: CVE-2022-36063
Aliases: GHSA-chpp-5fv9-6368
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2022-10-10
Source: https://osv.dev/vulnerability/CVE-2022-36063
Type: osv

## Details
Azure RTOS USBx is a USB host, device, and on-the-go (OTG) embedded stack, fully integrated with Azure RTOS ThreadX and available for all Azure RTOS ThreadX–supported processors. Azure RTOS USBX implementation of host support for USB CDC ECM includes an integer underflow and a buffer overflow in the `_ux_host_class_cdc_ecm_mac_address_get` function which may be potentially exploited to achieve remote code execution or denial of service. Setting mac address string descriptor length to a `0` or `1` allows an attacker to introduce an integer underflow followed (string_length) by a buffer overflow of the `cdc_ecm -> ux_host_class_cdc_ecm_node_id` array. This may allow one to redirect the code execution flow or introduce a denial of service. The fix has been included in USBX release [6.1.12](https://github.com/azure-rtos/usbx/releases/tag/v6.1.12_rel). Improved mac address string descriptor length validation to check for unexpectedly small values may be used as a workaround.

## References
- https://github.com/azure-rtos/usbx/blob/master/common/usbx_host_classes/src/ux_host_class_cdc_ecm_mac_address_get.c#L264
- https://github.com/azure-rtos/usbx/releases/tag/v6.1.12_rel
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36063.json
- https://github.com/azure-rtos/usbx/security/advisories/GHSA-chpp-5fv9-6368
- https://nvd.nist.gov/vuln/detail/CVE-2022-36063
