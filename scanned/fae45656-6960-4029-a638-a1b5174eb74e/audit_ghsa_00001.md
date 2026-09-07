# [H] OS Command Injection in craftercms:crafter-studio

## Summary
Severity: High
Advisory: GHSA-9fcp-vcq9-9h2h
CVE: CVE-2018-19907
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-19
Source: https://github.com/advisories/GHSA-9fcp-vcq9-9h2h
Type: github-advisory

## Affected
- Maven: `org.craftercms:crafter-studio` — affected >=0

## Details
A Server-Side Template Injection issue was discovered in Crafter CMS 3.0.18. Attackers with developer privileges may execute OS commands by Creating/Editing a template file (.ftl filetype) that triggers a call to freemarker.template.utility.Execute in the FreeMarker library during rendering of a web page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19907
- https://github.com/craftercms/craftercms/issues/2677
- https://github.com/advisories/GHSA-9fcp-vcq9-9h2h
- https://github.com/craftercms/craftercms
- https://medium.com/@buxuqua/rce-vulnerability-in-crafter-cms-server-side-template-injection-19d8708ce242
