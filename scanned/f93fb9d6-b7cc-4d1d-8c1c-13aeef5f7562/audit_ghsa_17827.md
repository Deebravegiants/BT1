# [H] Improper handling of case sensitivity in Jenkins OpenId Connect Authentication Plugin 

## Summary
Severity: High
Advisory: GHSA-q9cm-88jx-3vfw
CVE: CVE-2025-24399
CWE: CWE-178, CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-q9cm-88jx-3vfw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oic-auth` — affected >=0 <4.453.v4d7765c854f4

## Details
The Jenkins OpenId Connect Authentication Plugin 4.452.v2849b_d3945fa_ and earlier treats usernames as case-insensitive.

On a Jenkins instance configured with a case-sensitive OpenID Connect provider, this allows attackers to log in as any user by providing a username that differs only in letter case, potentially gaining administrator access to Jenkins.

OpenId Connect Authentication Plugin 4.453.v4d7765c854f4 introduces an advanced configuration option to manage username case sensitivity, with default to case-sensitive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24399
- https://github.com/jenkinsci/oic-auth-plugin/commit/4d7765c854f4f5e6e3c26ed950a26042a7527875
- https://github.com/jenkinsci/oic-auth-plugin
- https://www.jenkins.io/security/advisory/2025-01-22/#SECURITY-3461
