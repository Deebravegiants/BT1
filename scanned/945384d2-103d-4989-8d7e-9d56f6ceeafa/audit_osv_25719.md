# [M] Buffer overflow in Zephyr USB

## Summary
Severity: Medium
Advisory: CVE-2023-4265
Aliases: GHSA-4vgv-5r6q-r6xh
CVSS: 6.4 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2023-08-12
Source: https://osv.dev/vulnerability/CVE-2023-4265
Type: osv

## Details
Potential buffer overflow vulnerabilities in the following locations:
 https://github.com/zephyrproject-rtos/zephyr/blob/main/drivers/usb/device/usb_dc_native_posix.c#L359 https://github.com/zephyrproject-rtos/zephyr/blob/main/drivers/usb/device/usb_dc_native_posix.c#L359 
 https://github.com/zephyrproject-rtos/zephyr/blob/main/subsys/usb/device/class/netusb/function_rndis... https://github.com/zephyrproject-rtos/zephyr/blob/main/subsys/usb/device/class/netusb/function_rndis.c#L841

## References
- http://packetstormsecurity.com/files/175657/Zephyr-RTOS-3.x.0-Buffer-Overflows.html
- http://seclists.org/fulldisclosure/2023/Nov/1
- http://www.openwall.com/lists/oss-security/2023/11/07/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4265.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-4vgv-5r6q-r6xh
- https://nvd.nist.gov/vuln/detail/CVE-2023-4265
- https://github.com/zephyrproject-rtos/zephyr
