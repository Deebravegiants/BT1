# [H] Jenkins vSphere Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-2g32-2j8w-2qgf
CVE: CVE-2018-1000153
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2g32-2j8w-2qgf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vsphere-cloud` — affected >=0 <2.17

## Details
A cross-site request forgery vulnerability exists in Jenkins vSphere Plugin 2.16 and older in Clone.java, CloudSelectorParameter.java, ConvertToTemplate.java, ConvertToVm.java, Delete.java, DeleteSnapshot.java, Deploy.java, ExposeGuestInfo.java, FolderVSphereCloudProperty.java, PowerOff.java, PowerOn.java, Reconfigure.java, Rename.java, RenameSnapshot.java, RevertToSnapshot.java, SuspendVm.java, TakeSnapshot.java, VSphereBuildStepContainer.java, vSphereCloudProvisionedSlave.java, vSphereCloudSlave.java, vSphereCloudSlaveTemplate.java, VSphereConnectionConfig.java, vSphereStep.java that allows attackers to perform form validation related actions, including sending numerous requests to the configured vSphere server, potentially resulting in denial of service, or send credentials stored in Jenkins with known ID to an attacker-specified server ("test connection"). Additionally, these form validation methods did not require POST requests, resulting in a CSRF vulnerability. As of version 2.17, these form validation methods require POST requests and appropriate user permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000153
- https://github.com/jenkinsci/vsphere-cloud-plugin
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-745
