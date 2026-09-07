# [M] Spoofing attack in swagger-ui-dist

## Summary
Severity: Medium
Advisory: GHSA-6c9x-mj3g-h47x
CVE: CVE-2021-46708
CWE: CWE-1021
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-6c9x-mj3g-h47x
Type: github-advisory

## Affected
- npm: `swagger-ui-dist` — affected >=0 <4.1.3

## Details
The swagger-ui-dist package before 4.1.3 for Node.js could allow a remote attacker to hijack the clicking action of the victim. By persuading a victim to visit a malicious Web site, a remote attacker could exploit this vulnerability to hijack the victim's click actions and possibly launch further attacks against the victim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46708
- https://github.com/swagger-api/swagger-ui
- https://security.netapp.com/advisory/ntap-20220407-0004
- https://security.snyk.io/vuln/SNYK-JS-SWAGGERUIDIST-2314884
- https://www.npmjs.com/package/swagger-ui-dist/v/4.1.3
