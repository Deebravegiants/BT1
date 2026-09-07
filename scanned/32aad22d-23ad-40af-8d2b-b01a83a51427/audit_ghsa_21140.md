# [M] CSRF vulnerability in Jenkins openstack-heat Plugin

## Summary
Severity: Medium
Advisory: GHSA-fqhm-fjjv-7q8x
CVE: CVE-2022-36911
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-fqhm-fjjv-7q8x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:openstack-heat` — affected >=0

## Details
openstack-heat Plugin 1.5 and earlier does not perform permission checks in methods implementing form validation.

This form validation methods do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36911
- https://github.com/jenkinsci/openstack-heat-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2105%20(1)
- http://www.openwall.com/lists/oss-security/2022/07/27/1
