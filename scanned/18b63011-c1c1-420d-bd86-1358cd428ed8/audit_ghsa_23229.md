# [M] Jenkins Redgate SQL Change Automation Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-9hpq-528p-48j3
CVE: CVE-2019-16557
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9hpq-528p-48j3
Type: github-advisory

## Affected
- Maven: `com.redgate.plugins.redgatesqlci:redgate-sql-ci` — affected >=0 <2.0.4

## Details
Jenkins Redgate SQL Change Automation Plugin 2.0.3 and earlier stores credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16557
- https://github.com/jenkinsci/redgate-sql-ci-plugin/commit/18525ee6f01a5bc36040d40f1ff63702ce7280ac
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1598
- http://www.openwall.com/lists/oss-security/2019/12/17/1
