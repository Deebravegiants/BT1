# [M] BIT-artifactory-2021-45074

## Summary
Severity: Medium
Advisory: BIT-artifactory-2021-45074
Aliases: CVE-2021-45074
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-artifactory-2021-45074
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=7.0.0 <7.29.3

## Details
JFrog Artifactory before 7.29.3 and 6.23.38, is vulnerable to Broken Access Control, a low-privileged user is able to delete other known users OAuth token, which will force a reauthentication on an active session or in the next UI session.

## References
- https://www.jfrog.com/confluence/display/JFROG/CVE-2021-45074%3A+Artifactory+Broken+Access+Control+on+Delete+OAuth+Tokens
- https://www.jfrog.com/confluence/display/JFROG/JFrog+Security+Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2021-45074
