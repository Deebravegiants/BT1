# [H] CVE-2018-16601

## Summary
Severity: High
Advisory: CVE-2018-16601
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-16601
Type: osv

## Details
An issue was discovered in Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware TCP/IP component. A crafted IP header triggers a full memory space copy in prvProcessIPPacket, leading to denial of service and possibly remote code execution.

## References
- https://blog.zimperium.com/freertos-tcpip-stack-vulnerabilities-put-wide-range-devices-risk-compromise-smart-homes-critical-infrastructure-systems/
- https://github.com/aws/amazon-freertos/blob/v1.3.2/CHANGELOG.md
- https://blog.zimperium.com/freertos-tcpip-stack-vulnerabilities-details/
