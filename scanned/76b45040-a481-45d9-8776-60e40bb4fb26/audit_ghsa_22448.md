# [H] CSRF vulnerability and missing permission checks in Openstack Cloud Plugin allowed capturing credentials 

## Summary
Severity: High
Advisory: GHSA-grf8-94q5-4phx
CVE: CVE-2018-1000603
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-grf8-94q5-4phx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:openstack-cloud` — affected >=0 <2.37

## Details
A exposure of sensitive information vulnerability exists in Jenkins Openstack Cloud Plugin 2.35 and earlier in BootSource.java, InstancesToRun.java, JCloudsCleanupThread.java, JCloudsCloud.java, JCloudsComputer.java, JCloudsPreCreationThread.java, JCloudsRetentionStrategy.java, JCloudsSlave.java, JCloudsSlaveTemplate.java, LauncherFactory.java, OpenstackCredentials.java, OpenStackMachineStep.java, SlaveOptions.java, SlaveOptionsDescriptor.java that allows attackers with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins, and to cause Jenkins to submit HTTP requests to attacker-specified URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000603
- https://github.com/jenkinsci/openstack-cloud-plugin/commit/7123cf70c5223f22b44a3c7e59255c6a6e44da8b
- https://github.com/jenkinsci/openstack-cloud-plugin/commit/9ec76f8db6aa5b9e868c5d7dade09f1ef1a0fdb6
- https://github.com/jenkinsci/openstack-cloud-plugin
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-808
