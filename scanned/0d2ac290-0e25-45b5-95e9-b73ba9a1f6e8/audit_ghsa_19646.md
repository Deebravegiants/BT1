# [M] Bare Metal Operator (BMO) can expose any secret from other namespaces via BMCEventSubscription CRD

## Summary
Severity: Medium
Advisory: GHSA-c98h-7hp9-v9hq
CVE: CVE-2025-29781
CWE: CWE-200, CWE-653
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-17
Source: https://github.com/advisories/GHSA-c98h-7hp9-v9hq
Type: github-advisory

## Affected
- Go: `github.com/metal3-io/baremetal-operator/apis` — affected >=0.9.0 <0.9.1
- Go: `github.com/metal3-io/baremetal-operator/apis` — affected >=0 <0.8.1

## Details
### Impact

The Bare Metal Operator (BMO) implements a Kubernetes API for managing bare metal hosts in Metal3. 

Baremetal Operator enables users to load Secret from arbitrary namespaces upon deployment of the namespace scoped Custom Resource `BMCEventSubscription` (BMCES). An adversary Kubernetes account with only namespace level roles (e.g. a tenant controlling a namespace) may create a BMCES in their authorized namespace and then load Secrets from their unauthorized namespaces to their authorized namespace via the Baremetal Operator controller's cluster scoped privileges, causing Secret leakage.

### Patches

The patch makes BMO refuse to read Secrets from other namespace than where the corresponding Bare Metal Host (BMH) resource is. The patch does not change the `BMCEventSubscription` API in BMO, but stricter validation will deny the request at admission time. It will also prevent the controller reading such Secrets, in case the BMCES resource has already been deployed.

The issue exists for all versions of BMO, and is patched in BMO releases v0.9.1 and v0.8.1. Prior upgrading to patched BMO version, duplicate any existing Secret pointed to by `BMCEventSubscription`'s `httpHeadersRef` to the same namespace where the corresponding BMH exists. After upgrade, remove the old Secrets.

### Workarounds

Operator can configure BMO RBAC to be namespace scoped, instead of cluster scoped, to prevent BMO from accessing Secrets from other namespaces, and/or use `WATCH_NAMESPACE` configuration option to limit BMO to single namespace.

### References

- [patch to main](https://github.com/metal3-io/baremetal-operator/commit/19f8443b1fe182f76dd81b43122e8dd102f8b94c)
- [patch to release-0.9](https://github.com/metal3-io/baremetal-operator/pull/2321)
- [patch to release-0.8](https://github.com/metal3-io/baremetal-operator/pull/2322)
- [BMCEventSubscription design document](https://github.com/metal3-io/metal3-docs/blob/main/design/baremetal-operator/bmc-events.md)

### Credits

Metal3 Security Team thanks [WHALEEYE](https://github.com/WHALEEYE) and [debuggerchen](https://github.com/debuggerchen) of [Lab for Internet and Security Technology](https://users.cs.northwestern.edu/~list/) for responsible vulnerability disclosure.

## References
- https://github.com/metal3-io/baremetal-operator/security/advisories/GHSA-c98h-7hp9-v9hq
- https://nvd.nist.gov/vuln/detail/CVE-2025-29781
- https://github.com/metal3-io/baremetal-operator/pull/2321
- https://github.com/metal3-io/baremetal-operator/pull/2322
- https://github.com/metal3-io/baremetal-operator/commit/19f8443b1fe182f76dd81b43122e8dd102f8b94c
- https://github.com/metal3-io/baremetal-operator
- https://github.com/metal3-io/metal3-docs/blob/main/design/baremetal-operator/bmc-events.md
