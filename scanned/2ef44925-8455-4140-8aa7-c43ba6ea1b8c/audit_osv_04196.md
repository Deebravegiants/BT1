# [H] BIT-artifactory-2020-2165

## Summary
Severity: High
Advisory: BIT-artifactory-2020-2165
Aliases: CVE-2020-2165, GHSA-xqf6-5grh-6223
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-artifactory-2020-2165
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=0 <3.6.1

## Details
Jenkins Artifactory Plugin 3.6.0 and earlier transmits configured passwords in plain text as part of its global Jenkins configuration form, potentially resulting in their exposure.

## References
- http://www.openwall.com/lists/oss-security/2020/03/25/2
- https://jenkins.io/security/advisory/2020-03-25/#SECURITY-1542%20%282%29
- https://nvd.nist.gov/vuln/detail/CVE-2020-2165
