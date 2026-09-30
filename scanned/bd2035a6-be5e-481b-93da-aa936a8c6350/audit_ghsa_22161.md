# [M] Jenkins Amazon EC2 Plugin leaked beginning of private key in system log

## Summary
Severity: Medium
Advisory: GHSA-w7fv-7j46-wwrv
CVE: CVE-2019-10364
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w7fv-7j46-wwrv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2` — affected >=0 <1.44

## Details
Jenkins Amazon EC2 Plugin printed a log message that contained the beginning of the private key to the Jenkins system log.

The log message no longer includes the beginning of the private key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10364
- https://github.com/jenkinsci/ec2-plugin/commit/78c3c49a227ac8eccb8b1be7193d5605363fe251
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-673
- http://www.openwall.com/lists/oss-security/2019/07/31/1
