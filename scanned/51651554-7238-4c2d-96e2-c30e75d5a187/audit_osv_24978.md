# [M] CVE-2023-29049

## Summary
Severity: Medium
Advisory: CVE-2023-29049
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-29049
Type: osv

## Details
The "upsell" widget at the portal page could be abused to inject arbitrary script code. Attackers that manage to lure users to a compromised account, or gain temporary access to a legitimate account, could inject script code to gain persistent code execution capabilities under a trusted domain. User input for this widget is now sanitized to avoid malicious content the be processed. No publicly available exploits are known.

## References
- http://packetstormsecurity.com/files/176421/OX-App-Suite-7.10.6-XSS-Command-Execution-LDAP-Injection.html
- http://seclists.org/fulldisclosure/2024/Jan/3
- https://documentation.open-xchange.com/appsuite/security/advisories/csaf/2023/oxas-adv-2023-0005.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29049.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29049
- https://software.open-xchange.com/products/appsuite/doc/Release_Notes_for_Patch_Release_6248_7.10.6_2023-09-19.pdf
