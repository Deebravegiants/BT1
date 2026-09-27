# [H] Improper handling of REST API XML deserialization errors in Jenkins

## Summary
Severity: High
Advisory: GHSA-qv6f-rcv6-6q3x
CVE: CVE-2021-21604
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qv6f-rcv6-6q3x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.275

## Details
Jenkins provides XML REST APIs to configure views, jobs, and other items. When deserialization fails because of invalid data, Jenkins 2.274 and earlier, LTS 2.263.1 and earlier stores invalid object references created through these endpoints in the Old Data Monitor. If an administrator discards the old data, some erroneous data submitted to these endpoints may be persisted.

This allows attackers with View/Create, Job/Create, Agent/Create, or their respective */Configure permissions to inject crafted content into Old Data Monitor that results in the instantiation of potentially unsafe objects when discarded by an administrator.\n\nJenkins 2.275, LTS 2.263.2 does not record submissions from users in Old Data Monitor anymore.

In case of problems, the [Java system properties](https://www.jenkins.io/doc/book/managing/system-properties/) `hudson.util.RobustReflectionConverter.recordFailuresForAdmins` and `hudson.util.RobustReflectionConverter.recordFailuresForAllAuthentications` can be set to true to record configuration data submissions from administrators or all users, partially or completely disabling this fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21604
- https://github.com/jenkinsci/jenkins/commit/f1056bd814fc1f19ea241a101d649b8c143807e7
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-1923
