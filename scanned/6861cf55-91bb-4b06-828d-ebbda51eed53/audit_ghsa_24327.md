# [H] Plaintext password storage in Jenkins InfluxDB Plugin

## Summary
Severity: High
Advisory: GHSA-rv97-r8f7-8wmg
CVE: CVE-2019-10329
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rv97-r8f7-8wmg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:influxdb` — affected >=0 <1.22

## Details
Jenkins InfluxDB Plugin Prior to 1.22 stored credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10329
- https://github.com/jenkinsci/influxdb-plugin/commit/bfc2fcc0d8e6fb6f2dff5a45353abac5cefc0573
- https://github.com/jenkinsci/influxdb-plugin
- https://jenkins.io/security/advisory/2019-05-31/#SECURITY-1403
- http://www.openwall.com/lists/oss-security/2019/05/31/2
- http://www.securityfocus.com/bid/108540
