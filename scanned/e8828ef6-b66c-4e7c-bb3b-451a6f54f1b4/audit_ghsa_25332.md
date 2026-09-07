# [H] Sandbox Bypass via CSRF in Jenkins Warnings Plugin 

## Summary
Severity: High
Advisory: GHSA-mmrv-3cqg-hpf9
CVE: CVE-2019-1003007
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mmrv-3cqg-hpf9
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:warnings` — affected >=0 <5.0.1

## Details
A cross-site request forgery vulnerability exists in Jenkins Warnings Plugin 5.0.0 and earlier in src/main/java/hudson/plugins/warnings/GroovyParser.java that allows attackers to execute arbitrary code via a form validation HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003007
- https://github.com/jenkinsci/warnings-plugin
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1295%20%281%29
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1295%20(1)
