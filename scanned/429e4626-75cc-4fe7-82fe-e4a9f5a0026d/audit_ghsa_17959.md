# [H] External Secrets Operator's Missing Namespace Restriction Allows Unauthorized Secret Access

## Summary
Severity: High
Advisory: GHSA-fcxq-v2r3-cc8h
CVE: CVE-2025-55196
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-fcxq-v2r3-cc8h
Type: github-advisory

## Affected
- Go: `github.com/external-secrets/external-secrets` — affected >=0.15.0 <0.19.2

## Details
## Summary
A vulnerability was discovered in the External Secrets Operator where the `List()` calls for Kubernetes Secret and SecretStore resources performed by the `PushSecret` controller did not apply a namespace selector.  
This flaw allowed an attacker to use label selectors to list and read secrets/secret-stores across the cluster, bypassing intended namespace restrictions.

---

## Impact
An attacker with the ability to create or update `PushSecret` resources and control `SecretStore` configurations could exploit this vulnerability to exfiltrate sensitive data from arbitrary namespaces.  
This could lead to full disclosure of Kubernetes secrets, including credentials, tokens, and other sensitive information stored in the cluster.

---

## Exploitability
To exploit this vulnerability, an attacker must:

1. Have permissions to create or update `PushSecret` resources.
2. Control one or more `SecretStore` resources.

With these conditions met, the attacker could leverage label selectors to list secrets from any namespace and retrieve their contents.

---

## Affected Versions
- **Vulnerable:** v0.15.0 – v0.19.1  
- **Not Vulnerable:** v0.19.2 and later  

---

## Fix
The vulnerability was addressed in v0.19.2 by adding namespace restrictions to the `List()` calls for both `PushSecret` and `SecretStore` controllers.  
This ensures that only secrets in the intended namespace are accessible.

Relevant fixes:
- [#5133](https://github.com/external-secrets/external-secrets/pull/5133) – Enforce namespace selector for PushSecret `List()` calls  
- [#5109](https://github.com/external-secrets/external-secrets/pull/5109) – Enforce namespace selector for SecretStore `List()` calls  

---

## Mitigation
If upgrading to v0.19.2 or later is not immediately possible, the following mitigations are recommended:

- Restrict RBAC permissions so that only trusted service accounts can create or update `PushSecret` and `SecretStore` resources.  
- Audit existing `PushSecret` and `SecretStore` resources to ensure they are controlled by trusted parties.  
- Review Network Policies to prevent data exfiltration

---

## Credit
This vulnerability was reported by @gracedo and @moolen

## References
- https://github.com/external-secrets/external-secrets/security/advisories/GHSA-fcxq-v2r3-cc8h
- https://nvd.nist.gov/vuln/detail/CVE-2025-55196
- https://github.com/external-secrets/external-secrets/pull/5109
- https://github.com/external-secrets/external-secrets/pull/5133
- https://github.com/external-secrets/external-secrets/commit/39cdba5863533007b582dc63dd300839326b2f1d
- https://github.com/external-secrets/external-secrets/commit/de40e8f4fa9559c1d770bb674589b285da5ef2d1
- https://github.com/external-secrets/external-secrets
