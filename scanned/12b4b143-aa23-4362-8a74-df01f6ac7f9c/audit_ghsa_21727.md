# [H] Insecure template handling in Express-handlebars

## Summary
Severity: High
Advisory: GHSA-fr76-2wp8-fp92
CVE: CVE-2021-32820
CWE: CWE-200, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-fr76-2wp8-fp92
Type: github-advisory

## Affected
- npm: `express-handlebars` — affected >=0 <5.3.1

## Details
Express-handlebars is a Handlebars view engine for Express. Express-handlebars mixes pure template data with engine configuration options through the Express render API. More specifically, the layout parameter may trigger file disclosure vulnerabilities in downstream applications. This potential vulnerability is somewhat restricted in that only files with existing extentions (i.e. file.extension) can be included, files that lack an extension will have `.handlebars` appended to them. For complete details refer to the referenced GHSL-2021-018 report. Notes in documentation have been added to help users avoid this potential information exposure vulnerability.

A fix is discussed in https://github.com/express-handlebars/express-handlebars/pull/163

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32820
- https://github.com/express-handlebars/express-handlebars/pull/163
- https://github.com/express-handlebars/express-handlebars/commit/78c47a235c4ad7bc2674bddd8ec2721567ed8c72
- https://github.com/express-handlebars/express-handlebars#danger-
- https://github.com/express-handlebars/express-handlebars/blob/78c47a235c4ad7bc2674bddd8ec2721567ed8c72/README.md#danger-
- https://securitylab.github.com/advisories/GHSL-2021-018-express-handlebars
- https://www.npmjs.com/package/express-handlebars
