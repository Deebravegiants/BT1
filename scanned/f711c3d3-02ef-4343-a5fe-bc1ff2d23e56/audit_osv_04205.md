# [H] BIT-artifactory-2022-0573

## Summary
Severity: High
Advisory: BIT-artifactory-2022-0573
Aliases: CVE-2022-0573
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-artifactory-2022-0573
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=7.36.0 <7.36.1

## Details
JFrog Artifactory before 7.36.1 and 6.23.41, is vulnerable to Insecure Deserialization of untrusted data which can lead to DoS, Privilege Escalation and Remote Code Execution when a specially crafted request is sent by a low privileged authenticated user due to insufficient validation of a user-provided serialized object.

## References
- https://www.jfrog.com/confluence/display/JFROG/CVE-2022-0573%3A+Artifactory+Vulnerable+to+Deserialization+of+Untrusted+Data
- https://www.jfrog.com/confluence/display/JFROG/JFrog+Security+Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2022-0573
