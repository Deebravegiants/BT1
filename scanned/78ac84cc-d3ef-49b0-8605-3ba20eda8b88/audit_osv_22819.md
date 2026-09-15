# [H] Azure RTOS USBX Host PIMA vulnerable to read integer underflow with buffer overflow

## Summary
Severity: High
Advisory: CVE-2022-39293
Aliases: GHSA-gg76-h537-xq48
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2022-10-13
Source: https://osv.dev/vulnerability/CVE-2022-39293
Type: osv

## Details
Azure RTOS USBX is a high-performance USB host, device, and on-the-go (OTG) embedded stack, that is fully integrated with Azure RTOS ThreadX. The case is, in [_ux_host_class_pima_read](https://github.com/azure-rtos/usbx/blob/master/common/usbx_host_classes/src/ux_host_class_pima_read.c), there is data length from device response, returned in the very first packet, and read by [L165 code](https://github.com/azure-rtos/usbx/blob/082fd9db09a3669eca3358f10b8837a5c1635c0b/common/usbx_host_classes/src/ux_host_class_pima_read.c#L165), as header_length. Then in [L178 code](https://github.com/azure-rtos/usbx/blob/082fd9db09a3669eca3358f10b8837a5c1635c0b/common/usbx_host_classes/src/ux_host_class_pima_read.c#L178), there is a “if” branch, which check the expression of “(header_length - UX_HOST_CLASS_PIMA_DATA_HEADER_SIZE) > data_length” where if header_length is smaller than UX_HOST_CLASS_PIMA_DATA_HEADER_SIZE, calculation could overflow and then [L182 code](https://github.com/azure-rtos/usbx/blob/082fd9db09a3669eca3358f10b8837a5c1635c0b/common/usbx_host_classes/src/ux_host_class_pima_read.c#L182) the calculation of data_length is also overflow, this way the later [while loop start from L192](https://github.com/azure-rtos/usbx/blob/082fd9db09a3669eca3358f10b8837a5c1635c0b/common/usbx_host_classes/src/ux_host_class_pima_read.c#L192) can move data_pointer to unexpected address and cause write buffer overflow. The fix has been included in USBX release [6.1.12](https://github.com/azure-rtos/usbx/releases/tag/v6.1.12_rel). The following can be used as a workaround: Add check of `header_length`: 1. It must be greater than `UX_HOST_CLASS_PIMA_DATA_HEADER_SIZE`. 1. It should be greater or equal to the current returned data length (`transfer_request -> ux_transfer_request_actual_length`).

## References
- https://github.com/azure-rtos/usbx/releases/tag/v6.1.12_rel
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39293.json
- https://github.com/azure-rtos/usbx/security/advisories/GHSA-gg76-h537-xq48
- https://nvd.nist.gov/vuln/detail/CVE-2022-39293
