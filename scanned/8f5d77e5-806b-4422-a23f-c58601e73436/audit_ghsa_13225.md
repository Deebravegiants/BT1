# [H] Jenkins Google Login Plugin non-constant time token comparison

## Summary
Severity: High
Advisory: GHSA-g58x-57fv-86jh
CVE: CVE-2023-41936
CWE: CWE-697
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-g58x-57fv-86jh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-login` — affected >=0 <1.8

## Details
Jenkins Google Login Plugin 1.7 and earlier uses a non-constant time comparison function when checking whether the provided and expected token are equal, potentially allowing attackers to use statistical methods to obtain a valid token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41936
- https://github.com/jenkinsci/google-login-plugin/commit/2273af025ad06ee13ab73a5a070b10689c2db61e
- https://github.com/jenkinsci/google-login-plugin
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3228
- http://www.openwall.com/lists/oss-security/2023/09/06/9
