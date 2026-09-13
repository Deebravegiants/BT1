# [M] CVE-2018-16598

## Summary
Severity: Medium
Advisory: CVE-2018-16598
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-16598
Type: osv

## Details
An issue was discovered in Amazon Web Services (AWS) FreeRTOS through 1.3.1, FreeRTOS up to V10.0.1 (with FreeRTOS+TCP), and WITTENSTEIN WHIS Connect middleware TCP/IP component. In xProcessReceivedUDPPacket and prvParseDNSReply, any received DNS response is accepted, without confirming it matches a sent DNS request.

## References
- https://blog.zimperium.com/freertos-tcpip-stack-vulnerabilities-put-wide-range-devices-risk-compromise-smart-homes-critical-infrastructure-systems/
- https://github.com/aws/amazon-freertos/blob/v1.3.2/CHANGELOG.md
- https://blog.zimperium.com/freertos-tcpip-stack-vulnerabilities-details/
