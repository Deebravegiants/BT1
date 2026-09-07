# [H] Jenkins Simple Travis Pipeline Runner Plugin script sandbox bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-x7p9-vx6v-wv84
CVE: CVE-2019-10380
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x7p9-vx6v-wv84
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:simple-travis-runner` — affected >=0

## Details
Jenkins Simple Travis Pipeline Runner Plugin defines a custom list of pre-approved signatures for scripts protected by the Script Security sandbox.

This custom list of pre-approved signatures allows the use of methods that can be used to bypass Script Security sandbox protection. This results in arbitrary code execution on any Jenkins instance with this plugin installed.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10380
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-922
- http://www.openwall.com/lists/oss-security/2019/08/07/1
