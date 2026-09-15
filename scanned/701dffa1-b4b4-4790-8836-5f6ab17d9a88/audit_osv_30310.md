# [M] Semicolon Path Injection on API /api;/config

## Summary
Severity: Medium
Advisory: CVE-2024-50334
Aliases: GHSA-fhwp-f6g7-rr3p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50334
Type: osv

## Details
Scoold is a Q&A and a knowledge sharing platform for teams. A semicolon path injection vulnerability was found on the /api;/config endpoint. By appending a semicolon in the URL, attackers can bypass authentication and gain unauthorised access to sensitive configuration data. Furthermore, PUT requests on the /api;/config endpoint while setting the Content-Type: application/hocon header allow unauthenticated attackers to file reading via HOCON file inclusion. This allows attackers to retrieve sensitive information such as configuration files from the server, which can be leveraged for further exploitation. The vulnerability has been fixed in Scoold 1.64.0. A workaround would be to disable the Scoold API with scoold.api_enabled = false.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50334.json
- https://github.com/Erudika/scoold/security/advisories/GHSA-fhwp-f6g7-rr3p
- https://nvd.nist.gov/vuln/detail/CVE-2024-50334
