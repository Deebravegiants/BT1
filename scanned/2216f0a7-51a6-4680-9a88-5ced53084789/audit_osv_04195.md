# [M] BIT-artifactory-2020-2164

## Summary
Severity: Medium
Advisory: BIT-artifactory-2020-2164
Aliases: CVE-2020-2164, GHSA-4q47-ph87-fq4f
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-artifactory-2020-2164
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=0 <3.5.1

## Details
Jenkins Artifactory Plugin 3.5.0 and earlier stores its Artifactory server password unencrypted in its global configuration file on the Jenkins master where it can be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2020/03/25/2
- https://jenkins.io/security/advisory/2020-03-25/#SECURITY-1542%20%281%29
- https://nvd.nist.gov/vuln/detail/CVE-2020-2164
