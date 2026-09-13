# [M] Jenkins exposes multi-line secrets through error messages

## Summary
Severity: Medium
Advisory: GHSA-pj95-ph4q-4qm4
CVE: CVE-2024-47803
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-pj95-ph4q-4qm4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.462.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.466 <2.479

## Details
Jenkins 

Jenkins provides the `secretTextarea` form field for multi-line secrets.

Jenkins 2.478 and earlier, LTS 2.462.2 and earlier does not redact multi-line secret values in error messages generated for form submissions involving the `secretTextarea` form field.

This can result in exposure of multi-line secrets through those error messages, e.g., in the system log.

Jenkins 2.479, LTS 2.462.3 redacts multi-line secret values in error messages generated for form submissions involving the `secretTextarea` form field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47803
- https://www.jenkins.io/security/advisory/2024-10-02/#SECURITY-3451
