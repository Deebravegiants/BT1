# [H] BIT-artifactory-2023-42661

## Summary
Severity: High
Advisory: BIT-artifactory-2023-42661
Aliases: CVE-2023-42661
Ecosystem: Bitnami
Published: 2024-03-31
Source: https://osv.dev/vulnerability/BIT-artifactory-2023-42661
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=0 <7.76.2

## Details
JFrog Artifactory prior to version 7.76.2 is vulnerable to Arbitrary File Write of untrusted data, which may lead to DoS or Remote Code Execution when a specially crafted series of requests is sent by an authenticated user. This is due to insufficient validation of artifacts.

## References
- https://jfrog.com/help/r/jfrog-release-information/jfrog-security-advisories
- https://nvd.nist.gov/vuln/detail/CVE-2023-42661
