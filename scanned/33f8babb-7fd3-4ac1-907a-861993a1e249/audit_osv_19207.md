# [C] CVE-2020-8657

## Summary
Severity: Critical
Advisory: CVE-2020-8657
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-06
Source: https://osv.dev/vulnerability/CVE-2020-8657
Type: osv

## Details
An issue was discovered in EyesOfNetwork 5.3. The installation uses the same API key (hardcoded as EONAPI_KEY in include/api_functions.php for API version 2.4.2) by default for all installations, hence allowing an attacker to calculate/guess the admin access token.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-8657
- https://github.com/EyesOfNetworkCommunity/eonapi/issues/17
- http://packetstormsecurity.com/files/156605/EyesOfNetwork-AutoDiscovery-Target-Command-Execution.html
