# [C] CVE-2021-42553

## Summary
Severity: Critical
Advisory: CVE-2021-42553
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2021-42553
Type: osv

## Details
A buffer overflow vulnerability in stm32_mw_usb_host of STMicroelectronics in versions before 3.5.1 allows an attacker to execute arbitrary code when the descriptor contains more endpoints than USBH_MAX_NUM_ENDPOINTS. The library is typically integrated when using a RTOS such as FreeRTOS on STM32 MCUs.

## References
- https://github.com/STMicroelectronics/stm32_mw_usb_host/pull/4
- https://github.com/STMicroelectronics/stm32_mw_usb_host
