# [M] icingaweb2-module-jira template and field configuration are susceptible to CSRF

## Summary
Severity: Medium
Advisory: CVE-2023-30607
Aliases: GHSA-gh7w-7f7j-gwp5
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-30607
Type: osv

## Details
icingaweb2-module-jira provides integration with Atlassian Jira. Starting in version 1.3.0 and prior to version 1.3.2, template and field configuration forms perform the deletion action before user input is validated, including the cross site request forgery token. This issue is fixed in version 1.3.2. There are no known workarounds.

## References
- https://github.com/Icinga/icingaweb2-module-jira/releases/tag/v1.3.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30607.json
- https://github.com/Icinga/icingaweb2-module-jira/security/advisories/GHSA-gh7w-7f7j-gwp5
- https://nvd.nist.gov/vuln/detail/CVE-2023-30607
- https://github.com/Icinga/icingaweb2-module-jira/commit/7f0c53b7a3e87be2f4c2e8840805d7b7c9762424
