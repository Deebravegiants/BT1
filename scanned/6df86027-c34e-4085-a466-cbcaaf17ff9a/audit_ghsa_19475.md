# [H] Jenkins Templating Engine Plugin Vulnerable to Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-4vjp-327p-w4qv
CVE: CVE-2025-31722
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-4vjp-327p-w4qv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:templating-engine` — affected >=0 <2.5.4

## Details
Jenkins Templating Engine Plugin allows defining libraries both in the global configuration, as well as scoped to folders containing the pipelines using them. While libraries in the global configuration can only be set up by administrators and can therefore be trusted, libraries defined in folders can be configured by users with Item/Configure permission.

In Templating Engine Plugin 2.5.3 and earlier, libraries defined in folders are not subject to sandbox protection. This vulnerability allows attackers with Item/Configure permission to execute arbitrary code in the context of the Jenkins controller JVM.

In Templating Engine Plugin 2.5.4, libraries defined in folders are subject to sandbox protection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31722
- https://github.com/jenkinsci/templating-engine-plugin/commit/bb2b4468b3bf4cea494afb8549af4e6450972653
- https://github.com/jenkinsci/templating-engine-plugin
- https://www.jenkins.io/security/advisory/2025-04-02/#SECURITY-3505
