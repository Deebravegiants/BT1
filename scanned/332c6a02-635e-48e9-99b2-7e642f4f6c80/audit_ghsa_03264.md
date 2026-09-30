# [M] Insecure template handling in express-hbs

## Summary
Severity: Medium
Advisory: GHSA-rwxp-hwwf-653v
CVE: CVE-2021-32817
CWE: CWE-200, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-rwxp-hwwf-653v
Type: github-advisory

## Affected
- npm: `express-hbs` — affected >=0

## Details
express-hbs is an Express handlebars template engine. express-hbs mixes pure template data with engine configuration options through the Express render API. More specifically, the layout parameter may trigger file disclosure vulnerabilities in downstream applications. This potential vulnerability is somewhat restricted in that only files with existing extentions (i.e. file.extension) can be included, files that lack an extension will have .hbs appended to them. For complete details refer to the referenced GHSL-2021-019 report. Notes in documentation have been added to help users of express-hbs avoid this potential information exposure vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32817
- https://github.com/TryGhost/express-hbs/commit/ff6fad6e357699412d4e916273314e5e7af1500e
- https://github.com/TryGhost/express-hbs
- https://github.com/TryGhost/express-hbs#%EF%B8%8F-this-creates-a-potential-security-vulnerability
- https://securitylab.github.com/advisories/GHSL-2021-019-express-hbs
- https://www.npmjs.com/package/express-hbs
