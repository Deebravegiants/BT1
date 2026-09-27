# [M] CVE-2026-26399

## Summary
Severity: Medium
Advisory: CVE-2026-26399
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-26399
Type: osv

## Details
A stack-use-after-return issue exists in the Arduino_Core_STM32 library prior to version 1.7.0. The pwm_start() function allocates a TIM_HandleTypeDef structure on the stack and passes its address to HAL initialization routines, where it is stored in a global timer handle registry. After the function returns, interrupt service routines may dereference this dangling pointer, resulting in memory corruption.

## References
- https://github.com/stm32duino/Arduino_Core_STM32/releases/tag/1.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26399.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26399
- https://github.com/Acen28/CVE-2026-26399-Disclosure
