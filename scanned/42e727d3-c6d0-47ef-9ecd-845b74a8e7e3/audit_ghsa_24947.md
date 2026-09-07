# [M] Jenkins Lockable Resources Plugin XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wqjj-c9cx-q7cf
CVE: CVE-2019-1003042
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wqjj-c9cx-q7cf
Type: github-advisory

## Affected
- Maven: `org.6wind.jenkins:lockable-resources` — affected >=0 <2.5

## Details
A cross site scripting vulnerability in Jenkins Lockable Resources Plugin 2.4 and earlier allows attackers able to control resource names to inject arbitrary JavaScript in web pages rendered by the plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003042
- https://github.com/jenkinsci/lockable-resources-plugin/commit/4f401e250eb9e865e951b069255fea7052423739
- https://access.redhat.com/errata/RHSA-2019:1423
- https://github.com/jenkinsci/lockable-resources-plugin
- https://jenkins.io/security/advisory/2019-03-25/#SECURITY-1361
- http://www.openwall.com/lists/oss-security/2019/03/28/2
- http://www.securityfocus.com/bid/107628
