# [M] Ironic Standalone Operator's controller modifies user-owned resources without consent

## Summary
Severity: Medium
Advisory: GHSA-hfc8-w5f4-3x6m
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-hfc8-w5f4-3x6m
Type: github-advisory

## Affected
- Go: `github.com/metal3-io/ironic-standalone-operator` — affected >=0 <0.7.3
- Go: `github.com/metal3-io/ironic-standalone-operator` — affected >=0.8.0 <0.8.2

## Details
## Impact

The Ironic Standalone Operator (IRSO) is the operator to maintain an Ironic deployment for Metal3. IRSO controller automatically adds its environment label to user-provided Secrets and ConfigMaps without the resource owner's consent. A high-privilege controller modifying user-owned resources constitutes an unauthorized integrity violation. Deployments running IrSO v0.7.0 through v0.8.1 that reference user-provided Secrets or ConfigMaps (TLS certificates, BMC CA, trusted CA) are affected.

## Patches

Fixed in v0.9.0, v0.8.2, v0.7.3. 

## Workarounds

Manually add the environment label (ironic-standalone-operator.metal3.io/environment) to all user-provided Secrets and ConfigMaps before they are referenced in the Ironic resource. This prevents the controller from modifying them.

## Resources

- https://github.com/metal3-io/ironic-standalone-operator/pull/619
- https://github.com/metal3-io/ironic-standalone-operator/pull/664
- https://github.com/metal3-io/ironic-standalone-operator/pull/665

## References
- https://github.com/metal3-io/ironic-standalone-operator/security/advisories/GHSA-hfc8-w5f4-3x6m
- https://github.com/metal3-io/ironic-standalone-operator/pull/619
- https://github.com/metal3-io/ironic-standalone-operator/pull/664
- https://github.com/metal3-io/ironic-standalone-operator/pull/665
- https://github.com/metal3-io/ironic-standalone-operator
