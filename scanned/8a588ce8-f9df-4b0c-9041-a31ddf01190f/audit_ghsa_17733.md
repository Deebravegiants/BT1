# [M] Disabled permissions can be granted by Folder-based in Jenkins Authorization Strategy Plugin

## Summary
Severity: Medium
Advisory: GHSA-969g-rq57-c79h
CVE: CVE-2025-24401
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-969g-rq57-c79h
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:folder-auth` — affected >=0

## Details
Jenkins Folder-based Authorization Strategy Plugin 217.vd5b_18537403e and earlier does not verify that permissions configured to be granted are enabled, potentially allowing users formerly granted (typically optional permissions, like Overall/Manage) to access functionality they're no longer entitled to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24401
- https://github.com/jenkinsci/folder-auth-plugin
- https://www.jenkins.io/security/advisory/2025-01-22/#SECURITY-3062
