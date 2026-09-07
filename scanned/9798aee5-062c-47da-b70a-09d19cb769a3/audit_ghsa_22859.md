# [H] Elefant CMS CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-79m2-h67v-35q7
CVE: CVE-2018-16387
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-79m2-h67v-35q7
Type: github-advisory

## Affected
- Packagist: `elefant/cms` — affected >=0 <2.0.5

## Details
An issue was discovered in Elefant CMS before 2.0.5. There is a CSRF vulnerability that can add an account via user/add.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16387
- https://github.com/jbroadway/elefant/issues/285
