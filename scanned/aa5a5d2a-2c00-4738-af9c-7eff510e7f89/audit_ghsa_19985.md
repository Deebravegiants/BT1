# [H] Jenkins Custom Build Properties Plugin vulnerable to Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-5g2c-j6v9-vf94
CVE: CVE-2022-46686
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-5g2c-j6v9-vf94
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:custom-build-properties` — affected >=0 <2.82.v16d5b

## Details
Jenkins Custom Build Properties Plugin 2.79.vc095ccc85094 and earlier does not escape property values and build display names on the Custom Build Properties and Build Summary pages, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to set or change these values. Custom Build Properties Plugin 2.82.v16d5b_d3590c7 escapes property values and build display names on the Custom Build Properties and Build Summary pages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46686
- https://github.com/jenkinsci/custom-build-properties-plugin/commit/ff4e27181389955cbb051c1c91f0c85c6adbced0
- https://github.com/jenkinsci/custom-build-properties-plugin
- https://www.jenkins.io/security/advisory/2022-12-07/#SECURITY-2810
