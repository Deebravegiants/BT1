# [H] CVE-2021-45907

## Summary
Severity: High
Advisory: CVE-2021-45907
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-28
Source: https://osv.dev/vulnerability/CVE-2021-45907
Type: osv

## Details
An issue was discovered in gif2apng 1.9. There is a stack-based buffer overflow involving a for loop. An attacker has little influence over the data written to the stack, making it unlikely that the flow of control can be subverted.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1002669
