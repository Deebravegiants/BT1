# [H] Zen Cart findPluginAdminPage Local File Inclusion Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-5762
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2024-5762
Type: osv

## Details
Zen Cart findPluginAdminPage Local File Inclusion Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Zen Cart. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the findPluginAdminPage function. The issue results from the lack of proper validation of user-supplied data prior to passing it to a PHP include function. An attacker can leverage this in conjunction with other vulnerabilities to execute arbitrary code in the context of the service account. Was ZDI-CAN-21408.

## References
- https://docs.zen-cart.com/release/whatsnew_2.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5762.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5762
- https://www.zerodayinitiative.com/advisories/ZDI-24-883/
