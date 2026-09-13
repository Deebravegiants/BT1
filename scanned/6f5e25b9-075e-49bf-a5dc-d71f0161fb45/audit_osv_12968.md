# [M] CVE-2018-16603

## Summary
Severity: Medium
Advisory: CVE-2018-16603
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-16603
Type: osv

## Details
An issue was discovered in Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware TCP/IP component. Out of bounds access to TCP source and destination port fields in xProcessReceivedTCPPacket can leak data back to an attacker.

## References
- https://blog.zimperium.com/freertos-tcpip-stack-vulnerabilities-put-wide-range-devices-risk-compromise-smart-homes-critical-infrastructure-systems/
- https://github.com/aws/amazon-freertos/blob/v1.3.2/CHANGELOG.md
- https://blog.zimperium.com/freertos-tcpip-stack-vulnerabilities-details/
