# [H] Jenkins Configuration as Code Plugin has Insufficiently Protected Credentials

## Summary
Severity: High
Advisory: GHSA-8486-h39x-cx2f
CVE: CVE-2018-1000610
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8486-h39x-cx2f
Type: github-advisory

## Affected
- Maven: `io.jenkins:configuration-as-code` — affected >=0 <0.8-alpha

## Details
A exposure of sensitive information vulnerability exists in Jenkins Configuration as Code Plugin 0.7-alpha and earlier in DataBoundConfigurator.java, Attribute.java, BaseConfigurator.java, ExtensionConfigurator.java that allows attackers with access to Jenkins log files to obtain the passwords configured using Configuration as Code Plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000610
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-929
