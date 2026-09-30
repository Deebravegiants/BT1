# [M] Jenkins vSphere Plugin incorrect authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-48pq-x3vw-4pqf
CVE: CVE-2018-1000152
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-48pq-x3vw-4pqf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vsphere-cloud` — affected >=0 <2.17

## Details
An improper authorization vulnerability exists in Jenkins vSphere Plugin 2.16 and older in Clone.java, CloudSelectorParameter.java, ConvertToTemplate.java, ConvertToVm.java, Delete.java, DeleteSnapshot.java, Deploy.java, ExposeGuestInfo.java, FolderVSphereCloudProperty.java, PowerOff.java, PowerOn.java, Reconfigure.java, Rename.java, RenameSnapshot.java, RevertToSnapshot.java, SuspendVm.java, TakeSnapshot.java, VSphereBuildStepContainer.java, vSphereCloudProvisionedSlave.java, vSphereCloudSlave.java, vSphereCloudSlaveTemplate.java, VSphereConnectionConfig.java, vSphereStep.java that allows attackers to perform form validation related actions, including sending numerous requests to the configured vSphere server, potentially resulting in denial of service, or send credentials stored in Jenkins with known ID to an attacker-specified server ("test connection"). As of version 2.17, these form validation methods require POST requests and appropriate user permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000152
- https://github.com/jenkinsci/vsphere-cloud-plugin
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-745
