# [M] BIT-artifactory-2021-41834

## Summary
Severity: Medium
Advisory: BIT-artifactory-2021-41834
Aliases: CVE-2021-41834
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-artifactory-2021-41834
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=7.0.0 <7.28.0

## Details
JFrog Artifactory prior to version 7.28.0 and 6.23.38, is vulnerable to Broken Access Control, the copy functionality can be used by a low-privileged user to read and copy any artifact that exists in the Artifactory deployment due to improper permissions validation.

## References
- https://www.jfrog.com/confluence/display/JFROG/CVE-2021-41834%3A+Artifactory+Broken+Access+Control+on+Copy+Artifact
- https://nvd.nist.gov/vuln/detail/CVE-2021-41834
