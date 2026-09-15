# [H] OS Command Injection in Jenkins

## Summary
Severity: High
Advisory: GHSA-j472-mcq2-95p6
CVE: CVE-2017-1000393
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j472-mcq2-95p6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.73.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.74 <2.84

## Details
Jenkins 2.73.1 and earlier, 2.83 and earlier users with permission to create or configure agents in Jenkins could configure a launch method called 'Launch agent via execution of command on master'. This allowed them to run arbitrary shell commands on the master node whenever the agent was supposed to be launched. Configuration of this launch method now requires the Run Scripts permission typically only granted to administrators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000393
- https://github.com/jenkinsci/jenkins/commit/67f68c181033cbabf2075769e0f846f58c226c08
- https://github.com/jenkinsci/jenkins/commit/d7ea3f40efedd50541a57b943d5f7bbed046d091
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-10-11
