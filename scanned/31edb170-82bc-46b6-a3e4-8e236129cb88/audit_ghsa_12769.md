# [M] Exposure of system-scoped Kubernetes credentials in Jenkins Kubernetes Credentials Provider Plugin

## Summary
Severity: Medium
Advisory: GHSA-2jpx-h8j2-g8m4
CVE: CVE-2023-24425
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-2jpx-h8j2-g8m4
Type: github-advisory

## Affected
- Maven: `com.cloudbees.jenkins.plugins:kubernetes-credentials-provider` — affected >=0 <1.209.v862c6e5fb

## Details
Jenkins Kubernetes Credentials Provider Plugin 1.208.v128ee9800c04 and earlier does not set the appropriate context for Kubernetes credentials lookup, allowing attackers with Item/Configure permission to access and potentially capture Kubernetes credentials they are not entitled to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24425
- https://github.com/jenkinsci/kubernetes-credentials-provider-plugin/commit/862c6e5fb1ef65968ebfa399239cbef4fff7afc6
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-3022
