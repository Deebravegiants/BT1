# [M] ExternalSecrets vulnerable to privilege escalation with secret overwriting

## Summary
Severity: Medium
Advisory: GHSA-fq7h-9x26-6j22
CVE: CVE-2026-42876
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-fq7h-9x26-6j22
Type: github-advisory

## Affected
- Go: `github.com/external-secrets/external-secrets/apis` — affected >=0.1.0 <2.4.1

## Details
ExternalSecrets allows users to craft Service Account tokens for misconfigured Service Accounts in namespaces the users have access to.

### Impact

A user who only has permission to create ExternalSecret resources can cause the operator to create a Secret that Kubernetes will automatically populate with a long-lived token for the sepcified service account. This effectively allows the user to impersonate any service account in the namespace without needing direct create permissions on TokenRequest or Secrets of that type.

The problem is mitigated in severity by the fact that the user must have pre-existing permissions already at almost the same level as the escalation later gives. The attacker cannot use this method to gain access to more information without other things also being misconfigured in the ESO installation.

### Patches

Disallow this combination including the bootstrap token secret type.

### Workarounds

* Add admission control logic to prevent the use of Templates targeting undesired Types
* Remove Service Account Token generation via kube-controller-manager flags
* Restrict User RBAC on production clusters and sensitive namespaces

## References
- https://github.com/external-secrets/external-secrets/security/advisories/GHSA-fq7h-9x26-6j22
- https://nvd.nist.gov/vuln/detail/CVE-2026-42876
- https://github.com/external-secrets/external-secrets/commit/4ddd240af7fe88725d9857b9a0c198073502e288
- https://github.com/external-secrets/external-secrets
- https://github.com/external-secrets/external-secrets/releases/tag/v2.4.1
