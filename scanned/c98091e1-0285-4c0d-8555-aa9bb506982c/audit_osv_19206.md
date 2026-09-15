# [C] CVE-2020-8656

## Summary
Severity: Critical
Advisory: CVE-2020-8656
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-07
Source: https://osv.dev/vulnerability/CVE-2020-8656
Type: osv

## Details
An issue was discovered in EyesOfNetwork 5.3. The EyesOfNetwork API 2.4.2 is prone to SQL injection, allowing an unauthenticated attacker to perform various tasks such as authentication bypass via the username field to getApiKey in include/api_functions.php.

## References
- https://github.com/EyesOfNetworkCommunity/eonapi/issues/16
- http://packetstormsecurity.com/files/156266/EyesOfNetwork-5.3-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/156605/EyesOfNetwork-AutoDiscovery-Target-Command-Execution.html
