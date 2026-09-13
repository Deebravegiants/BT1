# [H] CVE-2020-8655

## Summary
Severity: High
Advisory: CVE-2020-8655
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-07
Source: https://osv.dev/vulnerability/CVE-2020-8655
Type: osv

## Details
An issue was discovered in EyesOfNetwork 5.3. The sudoers configuration is prone to a privilege escalation vulnerability, allowing the apache user to run arbitrary commands as root via a crafted NSE script for nmap 7.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-8655
- http://packetstormsecurity.com/files/156266/EyesOfNetwork-5.3-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/156605/EyesOfNetwork-AutoDiscovery-Target-Command-Execution.html
- https://github.com/EyesOfNetworkCommunity/eonconf/issues/8
