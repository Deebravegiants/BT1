# [C] Jenkins OpenID Connect Provider Plugin Incorrectly Validates Crafted Build ID Tokens

## Summary
Severity: Critical
Advisory: GHSA-q7c3-x7hm-qq72
CVE: CVE-2025-47884
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-q7c3-x7hm-qq72
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:oidc-provider` — affected >=0 <111.v29fd614b_3617

## Details
In Jenkins OpenID Connect Provider Plugin 96.vee8ed882ec4d and earlier the generation of build ID Tokens uses potentially overridden values of environment variables, in conjunction with certain other plugins allowing attackers able to configure jobs to craft a build ID Token that impersonates a trusted job, potentially gaining unauthorized access to external services.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47884
- https://github.com/jenkinsci/oidc-provider-plugin/commit/29fd614b36171048ddc78a995ce44bd12bd7997d
- https://github.com/jenkinsci/oidc-provider-plugin
- https://github.com/jenkinsci/oidc-provider-plugin/releases/tag/111.v29fd614b_3617
- https://www.jenkins.io/security/advisory/2025-05-14/#SECURITY-3574
