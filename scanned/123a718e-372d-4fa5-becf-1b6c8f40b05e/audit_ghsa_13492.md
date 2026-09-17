# [H] ThingsBoard Server-Side Template Injection

## Summary
Severity: High
Advisory: GHSA-6pgr-j9v4-xfvv
CVE: CVE-2023-45303
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-06
Source: https://github.com/advisories/GHSA-6pgr-j9v4-xfvv
Type: github-advisory

## Affected
- Maven: `org.thingsboard:thingsboard` — affected >=0 <3.5

## Details
ThingsBoard before 3.5 allows Server-Side Template Injection if users are allowed to modify an email template, because Apache FreeMarker supports `freemarker.template.utility.Execute` for content sent to the `/api/admin/settings` endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45303
- https://freemarker.apache.org/docs/api/freemarker/template/utility/Execute.html
- https://herolab.usd.de/security-advisories/usd-2023-0010
