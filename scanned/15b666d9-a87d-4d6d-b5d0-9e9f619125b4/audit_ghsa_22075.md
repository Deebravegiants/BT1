# [M] Stored XSS vulnerability in Jenkins Link Column Plugin

## Summary
Severity: Medium
Advisory: GHSA-q2mm-w3qc-2936
CVE: CVE-2020-2219
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q2mm-w3qc-2936
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:link-column` — affected >=0

## Details
Link Column Plugin allows users with View/Configure permission to add a new column to list views that contain a user-configurable link.\n\nLink Column Plugin 1.0 and earlier does not filter the URL for these links, allowing the `javascript:` scheme. This results in a stored cross-site scripting (XSS) vulnerability exploitable by users able to configure list views.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2219
- https://github.com/jenkinsci/link-column-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1803
- http://www.openwall.com/lists/oss-security/2020/07/02/7
