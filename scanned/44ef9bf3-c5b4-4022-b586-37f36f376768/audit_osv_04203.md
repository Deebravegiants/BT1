# [M] BIT-artifactory-2021-45730

## Summary
Severity: Medium
Advisory: BIT-artifactory-2021-45730
Aliases: CVE-2021-45730
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-artifactory-2021-45730
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=7.0.0 <7.31.10

## Details
JFrog Artifactory prior to 7.31.10, is vulnerable to Broken Access Control where a Project Admin is able to create, edit and delete Repository Layouts while Repository Layouts configuration should only be available for Platform Administrators.

## References
- https://www.jfrog.com/confluence/display/JFROG/CVE-2021-45730%3A+Artifactory+Broken+Access+Control+on+Repository+Layouts+Configuration
- https://nvd.nist.gov/vuln/detail/CVE-2021-45730
