# [M] Rancher exposes sensitive information through audit logs

## Summary
Severity: Medium
Advisory: GHSA-mw39-9qc2-f7mg
CVE: CVE-2024-58269
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-24
Source: https://github.com/advisories/GHSA-mw39-9qc2-f7mg
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=0 <0.0.0-20251013203444-50dc516a19ea

## Details
### Impact
**Note: The exploitation of this issue requires that the malicious user have access to Rancher’s audit log storage.**

A vulnerability has been identified in Rancher Manager, where sensitive information, including secret data, cluster import URLs, and registration tokens, is exposed to any entity with access to Rancher audit logs. This happens in two different ways:

1. Secret Annotation Leakage: When creating Kubernetes Secrets using the `stringData` field, the cleartext value is embedded in the `kubectl.kubernetes.io/last-applied-configuration` annotation. This annotation is included in Rancher audit logs within both the request and response bodies, exposing secret material that should be redacted.
2. Cluster Registration Token Leakage: During the import or creation of downstream clusters (Custom, Imported, or Harvester), Rancher audit logs record full cluster registration manifests and tokens, including:
a. Non-expiring import URLs such as `/v3/import/<token>_c-m-xxxx.yaml`.
b. Full `kubectl apply` and `curl` commands containing registration tokens and CA checksums.
c. Token values associated with cluster registration resources (`clusterRegistrationToken`).
d. These tokens are valid until explicitly revoked and can be used to re-register nodes, granting unauthorized cluster access.

An attacker or internal user who gains access to these logs could:
- Recover plaintext secret values from annotations.
- Use cluster registration tokens or import URLs to re-enroll agents or compromise downstream clusters.
- Access clusters that rely on these tokens for authentication, enabling lateral movement.

Please consult the associated  [MITRE ATT&CK - Technique - Log Enumeration](https://attack.mitre.org/techniques/T1654/) for further information about this category of attack.

### Patches
This vulnerability is addressed by applying redaction to sensitive information that was leaking.

Patched versions of Rancher include release `v2.12.3`.

### Workarounds
If the deployment can't be upgraded to a fixed version, users are encouraged to create `AuditPolicies` to redact and filter some of those requests as described in our [documentation](https://ranchermanager.docs.rancher.com/how-to-guides/advanced-user-guides/enable-api-audit-log#audit-log-policies).

The following AuditPolicy can be applied to redact the secrets:
```yaml
apiVersion: auditlog.cattle.io/v1
kind: AuditPolicy
metadata:
  name: redactions
spec:
  enabled: true
  additionalRedactions:
    - headers:
      - "Referer"
    - paths:
      - "$..metadata.annotations['kubectl.kubernetes.io/last-applied-configuration']"
```

Also consider granting access to Rancher's logs only for trusted users.


### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-mw39-9qc2-f7mg
- https://nvd.nist.gov/vuln/detail/CVE-2024-58269
- https://github.com/rancher/rancher/commit/26ad9216e94f77b5471f638256a6989030572adc
- https://github.com/rancher/rancher/commit/50dc516a19ea216e270f738912dc8d0c9ca99d5d
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2024-58269
- https://github.com/rancher/rancher
