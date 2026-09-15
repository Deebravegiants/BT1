# [H] Remote Code Execution using Server Side Template Injection in Peering Manager

## Summary
Severity: High
Advisory: CVE-2024-28114
Aliases: GHSA-q37x-qfrx-jcv6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N)
Published: 2024-03-12
Source: https://osv.dev/vulnerability/CVE-2024-28114
Type: osv

## Details
Peering Manager is a BGP session management tool. There is a Server Side Template Injection vulnerability that leads to Remote Code Execution in Peering Manager <=1.8.2. As a result arbitrary commands can be executed on the operating system that is running Peering Manager. This issue has been addressed in version 1.8.3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://owasp.org/www-community/attacks/Command_Injection
- https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/07-Input_Validation_Testing/18-Testing_for_Server_Side_Template_Injection
- https://stackoverflow.com/questions/73939573/how-to-sanitise-string-of-python-code-with-python
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28114.json
- https://github.com/peering-manager/peering-manager/security/advisories/GHSA-q37x-qfrx-jcv6
- https://nvd.nist.gov/vuln/detail/CVE-2024-28114
- https://github.com/peering-manager/peering-manager/commit/8a865fb596c11ad7caf45aef317d8fcbce7f85ff
