# [M] Insertion of Sensitive Information into Externally-Accessible File or Directory and Exposure of Sensitive Information to an Unauthorized Actor in hbs

## Summary
Severity: Medium
Advisory: GHSA-7f5c-rpf4-86p8
CVE: CVE-2021-32822
CWE: CWE-200, CWE-538, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-7f5c-rpf4-86p8
Type: github-advisory

## Affected
- npm: `hbs` — affected >=0

## Details
The npm hbs package is an Express view engine wrapper for Handlebars. Depending on usage, users of hbs may be vulnerable to a file disclosure vulnerability. There is currently no patch for this vulnerability. hbs mixes pure template data with engine configuration options through the Express render API. By overwriting internal configuration options a file disclosure vulnerability may be triggered in downstream applications. For an example PoC see the referenced GHSL-2021-020.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32822
- https://github.com/pillarjs/hbs
- https://securitylab.github.com/advisories/GHSL-2021-020-pillarjs-hbs
