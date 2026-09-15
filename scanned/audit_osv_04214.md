# [C] BIT-artifactory-2024-4142

## Summary
Severity: Critical
Advisory: BIT-artifactory-2024-4142
Aliases: CVE-2024-4142
Ecosystem: Bitnami
Published: 2024-05-03
Source: https://osv.dev/vulnerability/BIT-artifactory-2024-4142
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=7.78.0 <7.84.6

## Details
An Improper input validation vulnerability that could potentially lead to privilege escalation was discovered in JFrog Artifactory.

Due to this vulnerability, users with low privileges may gain administrative access to the system.

This issue can also be exploited in Artifactory platforms with anonymous access enabled.

## References
- https://jfrog.com/help/r/jfrog-release-information/jfrog-security-advisories
- https://nvd.nist.gov/vuln/detail/CVE-2024-4142
