# [M] IPAM controller service account granted unnecessary full access to Secrets

## Summary
Severity: Medium
Advisory: GHSA-49pm-43hf-6xfq
CVE: CVE-2026-47190
CWE: CWE-250
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-49pm-43hf-6xfq
Type: github-advisory

## Affected
- Go: `github.com/metal3-io/ip-address-manager` — affected >=0 <1.11.7
- Go: `github.com/metal3-io/ip-address-manager` — affected >=1.12.0 <1.12.4

## Details
### Impact

IPAM is the IP address Manager for Cluster API Provider Metal3. The IPAM controller's ClusterRole granted full CRUD permissions (create, delete, get, list, patch, update, watch) on core/v1 Secrets. The controller never accesses Secrets during normal operation. If the controller pod were compromised (e.g. via supply chain attack or container escape), an attacker could leverage these excessive  permissions to read, modify, or delete Secrets in the namespace, potentially exposing credentials and other sensitive data.

All users running ip-address-manager versions prior to the patched releases are affected.

### Patches

Fixed in:
- v1.11.7
- v1.12.4
- v1.13.0

Users should upgrade to the patched version for their release branch.

### Workarounds

Manually remove the Secrets resource entry from the metal3-ipam-controller-manager-role ClusterRole:

```yaml
# Remove this entire block from the ClusterRole
- apiGroups:
  - ""
  resources:
  - secrets
  verbs:
  - create
  - delete
  - get
  - list
  - patch
  - update
  - watch
```

### Resources

- https://github.com/metal3-io/ip-address-manager/pull/1355
- https://github.com/metal3-io/ip-address-manager/pull/1356 (backport to release-1.12)
- https://github.com/metal3-io/ip-address-manager/pull/1357 (backport to release-1.11)

## References
- https://github.com/metal3-io/ip-address-manager/security/advisories/GHSA-49pm-43hf-6xfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-47190
- https://github.com/metal3-io/ip-address-manager/pull/1355
- https://github.com/metal3-io/ip-address-manager/pull/1356
- https://github.com/metal3-io/ip-address-manager/pull/1357
- https://github.com/metal3-io/ip-address-manager
