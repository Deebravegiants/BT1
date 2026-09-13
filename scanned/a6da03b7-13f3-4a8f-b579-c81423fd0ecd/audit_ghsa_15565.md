# [M] The Bare Metal Operator (BMO) can expose particularly named secrets from other namespaces via BMH CRD

## Summary
Severity: Medium
Advisory: GHSA-pqfh-xh7w-7h3p
CVE: CVE-2024-43803
CWE: CWE-200, CWE-653
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-pqfh-xh7w-7h3p
Type: github-advisory

## Affected
- Go: `github.com/metal3-io/baremetal-operator` — affected >=0.7.0-rc.0 <0.8.0
- Go: `github.com/metal3-io/baremetal-operator` — affected >=0.6.0 <0.6.2
- Go: `github.com/metal3-io/baremetal-operator` — affected >=0 <0.5.2

## Details
### Impact
The Bare Metal Operator (BMO) implements a Kubernetes API for managing bare metal hosts in Metal3. The `BareMetalHost` (BMH) CRD allows the `userData`, `metaData`, and `networkData` for the provisioned host to be specified as links to Kubernetes Secrets. There are fields for both the `Name` and `Namespace` of the Secret, meaning that the baremetal-operator will read a `Secret` from any namespace. A user with access to create or edit a `BareMetalHost` can thus exfiltrate a `Secret` from another namespace by using it as e.g. the `userData` for provisioning some host (note that this need not be a real host, it could be a VM somewhere).

### Limiting factors
BMO will only read a key with the name `value` (or `userData`, `metaData`, or `networkData`), so that limits the exposure somewhat. `value` is probably a pretty common key though. Secrets used by _other_ `BareMetalHost`s in different namespaces are always vulnerable.

It is probably relatively unusual for anyone other than cluster administrators to have RBAC access to create/edit a `BareMetalHost`. This vulnerability is only meaningful, if the cluster has users other than administrators and users' privileges are limited to their respective namespaces.

### Patches
The patch prevents BMO from accepting links to Secrets from other namespaces as BMH input. Any BMH configuration is only read from the same namespace only.

The problem is patched in BMO releases v0.8.0, v0.6.2 and v0.5.2 and users should upgrade to those versions. Prior upgrading and if needed, duplicate the BMC Secrets to the namespace where the corresponding BMH is. After upgrade, remove the old Secrets.

### Workarounds
Operator can configure BMO RBAC to be namespace scoped for Secrets, instead of cluster scoped, to prevent BMO from accessing Secrets from other namespaces.

### References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43803
- https://github.com/metal3-io/baremetal-operator/pull/1929
- https://github.com/metal3-io/baremetal-operator/pull/1930
- https://github.com/metal3-io/baremetal-operator/pull/1931

## References
- https://github.com/metal3-io/baremetal-operator/security/advisories/GHSA-pqfh-xh7w-7h3p
- https://nvd.nist.gov/vuln/detail/CVE-2024-43803
- https://github.com/metal3-io/baremetal-operator/pull/1929
- https://github.com/metal3-io/baremetal-operator/pull/1930
- https://github.com/metal3-io/baremetal-operator/pull/1931
- https://github.com/metal3-io/baremetal-operator/commit/3af4882e9c5fadc1a7550f53daea21dccd271f74
- https://github.com/metal3-io/baremetal-operator/commit/bedae7b997d16f36e772806681569bb8eb4dadbb
- https://github.com/metal3-io/baremetal-operator/commit/c2b5a557641bc273367635124047d6c958aa15f7
- https://github.com/metal3-io/baremetal-operator
