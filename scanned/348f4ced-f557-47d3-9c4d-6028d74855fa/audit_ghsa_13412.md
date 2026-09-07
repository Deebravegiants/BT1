# [M] Jenkins Rebuilder Plugin vulnerable to Cross Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-5r5c-7rm4-mp4r
CVE: CVE-2023-37954
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-5r5c-7rm4-mp4r
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.hudson.plugins.rebuild:rebuild` — affected >=0

## Details
Jenkins Rebuilder Plugin 320.v5a_0933a_e7d61 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to rebuild a previous build.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37954
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3033
- http://www.openwall.com/lists/oss-security/2023/07/12/2
