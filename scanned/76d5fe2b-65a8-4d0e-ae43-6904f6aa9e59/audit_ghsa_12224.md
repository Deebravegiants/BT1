# [M] Moderate severity vulnerability that affects validator

## Summary
Severity: Medium
Advisory: GHSA-552w-rqg8-gxxm
CVE: CVE-2013-7453
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-552w-rqg8-gxxm
Type: github-advisory

## Affected
- npm: `validator` — affected >=0 <1.1.0

## Details
The validator module before 1.1.0 for Node.js allows remote attackers to bypass the cross-site scripting (XSS) filter via vectors related to UI redressing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7453
- https://github.com/advisories/GHSA-552w-rqg8-gxxm
- http://www.openwall.com/lists/oss-security/2016/04/20/11
