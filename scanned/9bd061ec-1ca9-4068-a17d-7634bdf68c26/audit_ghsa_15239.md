# [M] CSRF vulnerability in Jenkins GitLab Branch Source Plugin

## Summary
Severity: Medium
Advisory: GHSA-8r93-59cf-358f
CVE: CVE-2024-23902
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-8r93-59cf-358f
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:gitlab-branch-source` — affected >=0 <688.v5fa

## Details
Jenkins GitLab Branch Source Plugin 684.vea_fa_7c1e2fe3 and earlier does not require POST requests for a form validation endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to connect to an attacker-specified URL.

GitLab Branch Source Plugin 688.v5fa_356ee8520 requires POST requests for the affected form validation endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23902
- https://github.com/jenkinsci/gitlab-branch-source-plugin/commit/5fa356ee852091af900498db07259afe78d7aad2
- https://github.com/jenkinsci/gitlab-branch-source-plugin
- https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3251
- http://www.openwall.com/lists/oss-security/2024/01/24/6
