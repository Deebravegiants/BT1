# [M] Jenkins-image: sensitive data disclosure when using openshift jenkins image

## Summary
Severity: Medium
Advisory: BIT-jenkins-2024-9453
Aliases: CVE-2024-9453
Ecosystem: Bitnami
Published: 2025-08-19
Source: https://osv.dev/vulnerability/BIT-jenkins-2024-9453
Type: osv

## Affected
- Bitnami: `jenkins` — affected unspecified

## Details
A vulnerability was found in Red Hat OpenShift Jenkins. The bearer token is not obfuscated in the logs and potentially carries a high risk if those logs are centralized when collected. The token is typically valid for one year. This flaw allows a malicious user to jeopardize the environment if they have access to sensitive information.

## References
- https://access.redhat.com/security/cve/CVE-2024-9453
- https://bugzilla.redhat.com/show_bug.cgi?id=2316231
- https://nvd.nist.gov/vuln/detail/CVE-2024-9453
