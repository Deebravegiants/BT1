# [M] Jenkins Anchore Container Scanner Plugin vulnerable to Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-jg29-c2qj-wpm3
CVE: CVE-2019-16542
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jg29-c2qj-wpm3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:anchore-container-scanner` — affected >=0 <1.0.20

## Details
Jenkins Anchore Container Image Scanner Plugin 1.0.19 and earlier stores credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system. 

The credential being stored was a service password for the Anchore.io service. As the affected functionality has been deprecated, and the affected Anchore.io service has been shut down in late 2018, the affected feature has been removed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16542
- https://github.com/jenkinsci/anchore-container-scanner-plugin
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-1539
- http://www.openwall.com/lists/oss-security/2019/11/21/1
