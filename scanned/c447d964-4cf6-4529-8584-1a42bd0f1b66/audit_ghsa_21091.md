# [M] Jenkins Deployment Dashboard Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-5mxg-p5qh-2gch
CVE: CVE-2022-34796
CWE: CWE-522, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-5mxg-p5qh-2gch
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2-deployment-dashboard` — affected >=0

## Details
Jenkins Deployment Dashboard Plugin 1.0.10 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34796
- https://github.com/jenkinsci/ec2-deployment-dashboard
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2798%20%281%29
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2798%20(1)
