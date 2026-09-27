# [C] Deserialization of Untrusted Data in Jenkins

## Summary
Severity: Critical
Advisory: GHSA-26wc-3wqp-g3rp
CVE: CVE-2017-1000353
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-26wc-3wqp-g3rp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.50 <2.57
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.46.2

## Details
Jenkins versions 2.56 and earlier as well as 2.46.1 LTS and earlier are vulnerable to an unauthenticated remote code execution. An unauthenticated remote code execution vulnerability allowed attackers to transfer a serialized Java `SignedObject` object to the Jenkins CLI, that would be deserialized using a new `ObjectInputStream`, bypassing the existing blacklist-based protection mechanism. We're fixing this issue by adding `SignedObject` to the blacklist. We're also backporting the new HTTP CLI protocol from Jenkins 2.54 to LTS 2.46.2, and deprecating the remoting-based (i.e. Java serialization) CLI protocol, disabling it by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000353
- https://github.com/jenkinsci/jenkins/commit/36b8285a41eb28333549e8d851f81fd80a184076
- https://github.com/jenkinsci/jenkins/commit/f237601afd750a0eaaf961e8120b08de238f2c3f
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-04-26
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2017-1000353
- https://www.exploit-db.com/exploits/41965
- https://www.oracle.com/security-alerts/cpuapr2022.html
- http://packetstormsecurity.com/files/159266/Jenkins-2.56-CLI-Deserialization-Code-Execution.html
- http://www.securityfocus.com/bid/98056
