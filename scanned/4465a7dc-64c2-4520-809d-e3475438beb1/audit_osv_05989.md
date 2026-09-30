# [H] BIT-jenkins-2021-21686

## Summary
Severity: High
Advisory: BIT-jenkins-2021-21686
Aliases: CVE-2021-21686, GHSA-4g38-hrm4-rg94
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2021-21686
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.319.0

## Details
File path filters in the agent-to-controller security subsystem of Jenkins LTS 2.303.2 and earlier do not canonicalize paths, allowing operations to follow symbolic links to outside allowed directories.

## References
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455
- https://nvd.nist.gov/vuln/detail/CVE-2021-21686
