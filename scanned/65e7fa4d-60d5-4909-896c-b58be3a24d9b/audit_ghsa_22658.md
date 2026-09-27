# [M] Jenkins Email Extension Plugin showed plain text SMTP password in configuration form field

## Summary
Severity: Medium
Advisory: GHSA-gwxm-wqpq-w539
CVE: CVE-2018-1000176
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gwxm-wqpq-w539
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <2.62

## Details
An exposure of sensitive information vulnerability exists in Jenkins Email Extension Plugin 2.61 and older in src/main/resources/hudson/plugins/emailext/ExtendedEmailPublisher/global.groovy and ExtendedEmailPublisherDescriptor.java that allows attackers with control of a Jenkins administrator's web browser (e.g. malicious extension) to retrieve the configured SMTP password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000176
- https://jenkins.io/security/advisory/2018-04-16
