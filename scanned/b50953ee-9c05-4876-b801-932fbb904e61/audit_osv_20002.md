# [M] CVE-2021-29246

## Summary
Severity: Medium
Advisory: CVE-2021-29246
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-05
Source: https://osv.dev/vulnerability/CVE-2021-29246
Type: osv

## Details
BTCPay Server through 1.0.7.0 suffers from directory traversal, which allows an attacker with admin privileges to achieve code execution. The attacker must craft a malicious plugin file with special characters to upload the file outside of the restricted directory.

## References
- https://blog.btcpayserver.org/vulnerability-disclosure-v1-0-7-0/
- https://github.com/btcpayserver/btcpayserver/releases
