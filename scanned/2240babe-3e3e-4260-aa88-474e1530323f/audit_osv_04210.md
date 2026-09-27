# [M] BIT-artifactory-2023-42662

## Summary
Severity: Medium
Advisory: BIT-artifactory-2023-42662
Aliases: CVE-2023-42662
Ecosystem: Bitnami
Published: 2024-03-31
Source: https://osv.dev/vulnerability/BIT-artifactory-2023-42662
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=7.69.0 <7.71.8

## Details
JFrog Artifactory versions 7.59 and above, but below 7.59.18, 7.63.18, 7.68.19, 7.71.8 are vulnerable to an issue whereby user interaction with specially crafted URLs could lead to exposure of user access tokens due to improper handling of the CLI / IDE browser based SSO integration.

## References
- https://jfrog.com/help/r/jfrog-release-information/jfrog-security-advisories
- https://nvd.nist.gov/vuln/detail/CVE-2023-42662
