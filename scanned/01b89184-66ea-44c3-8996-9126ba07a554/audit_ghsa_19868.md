# [H] Jenkins AnchorChain Plugin Has a Cross-Site Scripting (XSS) Vulnerability

## Summary
Severity: High
Advisory: GHSA-xxrg-mg63-qfpj
CVE: CVE-2025-30196
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-xxrg-mg63-qfpj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:anchorchain` — affected 1.0

## Details
Jenkins AnchorChain Plugin 1.0 does not limit URL schemes for links it creates based on workspace content, allowing the javascript: scheme.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control the input file for the Anchor Chain post-build step.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30196
- https://github.com/jenkinsci/anchor-chain-plugin
- https://www.jenkins.io/security/advisory/2025-03-19/#SECURITY-3529
