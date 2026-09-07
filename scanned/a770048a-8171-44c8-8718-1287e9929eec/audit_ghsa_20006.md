# [M] Jenkins Google Login Plugin Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v93c-cxj5-c398
CVE: CVE-2022-46683
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-v93c-cxj5-c398
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-login` — affected >=1.4 <1.7

## Details
Jenkins Google Login Plugin 1.4 through 1.6 (both inclusive) improperly determines that a redirect URL after login is legitimately pointing to Jenkins. Google Login Plugin 1.7 only redirects to relative (Jenkins) URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46683
- https://github.com/jenkinsci/google-login-plugin/commit/532d714943ff8ae8dc862427d39a4b78b7f6a375
- https://github.com/jenkinsci/google-login-plugin
- https://www.jenkins.io/security/advisory/2022-12-07/#SECURITY-2967
