# [H] Command Injection in strapi

## Summary
Severity: High
Advisory: GHSA-9p2w-rmx4-9mw7
CVE: CVE-2019-19609
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-9p2w-rmx4-9mw7
Type: github-advisory

## Affected
- npm: `strapi` — affected >=0 <3.0.0-beta.17.8

## Details
Versions of `strapi` before 3.0.0-beta.17.8 are vulnerable to Command Injection. The package fails to sanitize plugin names in the `/admin/plugins/install/` route. This may allow an authenticated attacker with admin privileges to run arbitrary commands in the server.


## Recommendation

Upgrade to version 3.0.0-beta.17.8 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19609
- https://github.com/strapi/strapi/pull/4636
- https://bittherapy.net/post/strapi-framework-remote-code-execution
- https://github.com/strapi/strapi
- https://www.npmjs.com/advisories/1424
- http://packetstormsecurity.com/files/163940/Strapi-3.0.0-beta.17.7-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/163950/Strapi-CMS-3.0.0-beta.17.4-Remote-Code-Execution.html
