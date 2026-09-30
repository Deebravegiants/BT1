# [H] CVE-2018-16528

## Summary
Severity: High
Advisory: CVE-2018-16528
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-16528
Type: osv

## Details
Amazon Web Services (AWS) FreeRTOS through 1.3.1 allows remote attackers to execute arbitrary code because of mbedTLS context object corruption in prvSetupConnection and GGD_SecureConnect_Connect in AWS TLS connectivity modules.

## References
- https://blog.zimperium.com/freertos-tcpip-stack-vulnerabilities-details/
- https://blog.zimperium.com/freertos-tcpip-stack-vulnerabilities-put-wide-range-devices-risk-compromise-smart-homes-critical-infrastructure-systems/
- https://github.com/aws/amazon-freertos/blob/v1.3.2/CHANGELOG.md
