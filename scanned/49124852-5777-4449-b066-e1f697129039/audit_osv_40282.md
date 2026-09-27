# [C] Formie: Server-Side Template Injection in Formie Hidden field defaults

## Summary
Severity: Critical
Advisory: CVE-2026-52889
Aliases: GHSA-565m-g33j-jq96
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-52889
Type: osv

## Details
Formie is a Craft CMS plugin for creating forms. Prior to 3.1.27, Formie can pass request-derived Hidden field defaults such as HTTP User Agent, Referer URL, Current URL, Current URL without Query String, Query Parameter, and Cookie Value to Craft's Twig rendering layer during front-end form rendering. An unauthenticated attacker can place Twig syntax in one of these request-controlled inputs when a public form contains an affected Hidden field. Hidden::getFrontEndInputOptions() then assigns the value to defaultValue and calls renderString, causing server-side template evaluation rather than treating the request data as a plain string. Depending on the Craft site configuration and available Twig capabilities, exploitation can disclose sensitive information, modify application state, or achieve remote code execution. This issue is fixed in version 3.1.27.

## References
- https://github.com/verbb/formie/releases/tag/3.1.27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52889.json
- https://github.com/verbb/formie/security/advisories/GHSA-565m-g33j-jq96
- https://nvd.nist.gov/vuln/detail/CVE-2026-52889
- https://github.com/verbb/formie/commit/d3b9d15290405e484e3b5c91c5d8fab93047f9b2
