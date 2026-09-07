# [M] NASA Open MCT Cross Site Request Forgery (CSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4g88-4hgm-m99x
CVE: CVE-2023-45884
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-09
Source: https://github.com/advisories/GHSA-4g88-4hgm-m99x
Type: github-advisory

## Affected
- npm: `openmct` — affected >=0 <3.1.1

## Details
Cross Site Request Forgery (CSRF) vulnerability in NASA Open MCT (aka openmct) through 3.1.0 allows attackers to view sensitive information via the flexibleLayout plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45884
- https://github.com/nasa/openmct/pull/7148
- https://github.com/nasa/openmct/pull/7148/commits/4e95e12559c9c5364269ff366a59768573baacb4
- https://github.com/nasa/openmct
- https://www.linkedin.com/pulse/xss-nasas-open-mct-v302-visionspace-technologies-ubg4f
