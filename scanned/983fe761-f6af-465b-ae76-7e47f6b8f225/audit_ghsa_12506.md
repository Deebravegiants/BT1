# [M] Tokens stored in plain text by PaaSLane Estimate Plugin 

## Summary
Severity: Medium
Advisory: GHSA-c2f6-rf2r-6j6f
CVE: CVE-2023-50776
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-c2f6-rf2r-6j6f
Type: github-advisory

## Affected
- Maven: `com.cloudtp.jenkins:paaslane-estimate` — affected >=0

## Details
Jenkins PaaSLane Estimate Plugin 1.0.4 and earlier stores PaaSLane authentication tokens unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50776
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3182
- http://www.openwall.com/lists/oss-security/2023/12/13/4
