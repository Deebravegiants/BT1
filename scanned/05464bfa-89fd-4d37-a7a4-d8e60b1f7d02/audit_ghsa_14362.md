# [M] Ironic and ironic-inspector may expose as ConfigMaps

## Summary
Severity: Medium
Advisory: GHSA-9wh7-397j-722m
CVE: CVE-2023-30841
CWE: CWE-200, CWE-319
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-9wh7-397j-722m
Type: github-advisory

## Affected
- Go: `github.com/metal3-io/baremetal-operator` — affected >=0 <0.3.0

## Details
### Impact
Ironic and ironic-inspector deployed within Baremetal Operator using the included `deploy.sh` store their `.htpasswd` files as ConfigMaps instead of Secrets. This causes the plain-text username and hashed password to be readable by anyone having a cluster-wide read-access to the management cluster, or access to the management cluster's Etcd storage.

### Patches
This issue is patched in [baremetal-operator PR#1241](https://github.com/metal3-io/baremetal-operator/pull/1241), and is included in BMO release 0.3.0 onwards.

### Workarounds
User may modify the kustomizations and redeploy the BMO, or recreate the required ConfigMaps as Secrets per instructions in [baremetal-operator PR#1241](https://github.com/metal3-io/baremetal-operator/pull/1241)

## References
- https://github.com/metal3-io/baremetal-operator/security/advisories/GHSA-9wh7-397j-722m
- https://nvd.nist.gov/vuln/detail/CVE-2023-30841
- https://github.com/metal3-io/baremetal-operator/pull/1241
- https://github.com/metal3-io/baremetal-operator
