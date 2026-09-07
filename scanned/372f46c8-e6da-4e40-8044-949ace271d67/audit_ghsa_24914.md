# [M] Jenkins Google Play Android Publisher Plugin allows attacker to obtain credential IDs

## Summary
Severity: Medium
Advisory: GHSA-rvx4-gg8w-qw24
CVE: CVE-2018-1000109
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rvx4-gg8w-qw24
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-play-android-publisher` — affected >=0 <1.7

## Details
An improper authorization vulnerability exists in Jenkins Google Play Android Publisher Plugin version 1.6 and earlier in `GooglePlayBuildStepDescriptor.java` that allow an attacker to obtain credential IDs. As of version 1.7, enumeration of credentials IDs and validation of specified credentials in this plugin requires the permissions to have the ExtendedRead permission (when that permission is enabled; otherwise Configure permission) to the job in whose context credentials are being accessed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000109
- https://github.com/jenkinsci/google-play-android-publisher-plugin/commit/f81b058289caf3332ae40d599a36a3665b1fa13c
- https://github.com/jenkinsci/google-play-android-publisher-plugin
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-715
