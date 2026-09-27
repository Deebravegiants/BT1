# [H] Jenkins CloudBees CD Plugin vulnerable to arbitrary file deletion

## Summary
Severity: High
Advisory: GHSA-jx7x-rf3f-j644
CVE: CVE-2023-46654
CWE: CWE-22, CWE-59
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-jx7x-rf3f-j644
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:electricflow` — affected >=0 <1.1.33

## Details
In Jenkins CloudBees CD Plugin, artifacts that were previously copied from an agent to the controller are deleted after publishing by the 'CloudBees CD - Publish Artifact' post-build step.

CloudBees CD Plugin 1.1.32 and earlier follows symbolic links to locations outside of the expected directory during this cleanup process.

This allows attackers able to configure jobs to delete arbitrary files on the Jenkins controller file system.

CloudBees CD Plugin 1.1.33 deletes symbolic links without following them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46654
- https://github.com/jenkinsci/electricflow-plugin/commit/e45ca8428ae45f45ca07611e802eaa0f1484ab50
- https://github.com/jenkinsci/electricflow-plugin
- https://www.jenkins.io/security/advisory/2023-10-25/#SECURITY-3237
- http://www.openwall.com/lists/oss-security/2023/10/25/2
