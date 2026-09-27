# [H] CVE-2023-29048

## Summary
Severity: High
Advisory: CVE-2023-29048
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-29048
Type: osv

## Details
A component for parsing OXMF templates could be abused to execute arbitrary system commands that would be executed as the non-privileged runtime user. Users and attackers could run system commands with limited privilege to gain unauthorized access to confidential information and potentially violate integrity by modifying resources. The template engine has been reconfigured to deny execution of harmful commands on a system level. No publicly available exploits are known.

## References
- http://packetstormsecurity.com/files/176421/OX-App-Suite-7.10.6-XSS-Command-Execution-LDAP-Injection.html
- http://seclists.org/fulldisclosure/2024/Jan/3
- https://documentation.open-xchange.com/appsuite/security/advisories/csaf/2023/oxas-adv-2023-0005.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29048.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29048
- https://software.open-xchange.com/products/appsuite/doc/Release_Notes_for_Patch_Release_6248_7.10.6_2023-09-19.pdf
