# [M] Incorrect permission check in Jenkins GitLab Plugin allows enumerating credentials IDs 

## Summary
Severity: Medium
Advisory: GHSA-xhgq-h98j-859v
CVE: CVE-2025-24397
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-xhgq-h98j-859v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-plugin` — affected >=0 <1.9.7

## Details
The Jenkins GitLab Plugin 1.9.6 and earlier does not correctly perform a permission check in an HTTP endpoint.

This allows attackers with global Item/Configure permission (while lacking Item/Configure permission on any particular job) to enumerate credential IDs of GitLab API token credentials and Secret text credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credential IDs in GitLab Plugin 1.9.7 requires Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24397
- https://github.com/jenkinsci/gitlab-plugin
- https://www.jenkins.io/security/advisory/2025-01-22/#SECURITY-3260
