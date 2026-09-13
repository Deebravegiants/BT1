# [M] CAPM3 vulnerable to Cross-Namespace resource access

## Summary
Severity: Medium
Advisory: GHSA-rf84-wr5g-m3rp
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-rf84-wr5g-m3rp
Type: github-advisory

## Affected
- Go: `github.com/metal3-io/cluster-api-provider-metal3` — affected >=0 <1.11.8
- Go: `github.com/metal3-io/cluster-api-provider-metal3` — affected >=1.12.0 <1.12.5

## Details
## Summary

CAPM3 is Metal3's Cluster API (CAPI) provider for baremetal provisioning in Kubernetes. Multiple cross-namespace access control vulnerabilities in Cluster API Provider Metal3 allow users with permissions to create or modify CAPM3 resources in one namespace to reference, read, or claim resources belonging to other namespaces.

## Patched In

- **v1.13.0** (main branch — all fixes included)
- **v1.12.5** (all four fixes backported)
- **v1.11.8** (three of four fixes backported; Metal3DataClaim template restriction not applicable due to missing v1beta2 webhook infrastructure)

## Description

Four related vulnerabilities were identified and fixed:

### 1. Cross-namespace Secret references in Metal3Machine

Metal3Machine resources accepted userData, metaData, and networkData secret references pointing to arbitrary namespaces. A user could configure a Metal3Machine to  reference secrets in namespaces they do not have access to, and the controller would fetch and use those secrets.

### 2. Cross-namespace BareMetalHost lookups

The host annotation on Metal3Machine could include a namespace/name format, causing the controller to look up BareMetalHost resources in arbitrary namespaces. This  allowed a user to claim or associate with BareMetalHosts belonging to other tenants.

### 3. Incorrect logical operator in ConsumerRef validation

The Metal3LabelSync controller used AND logic (&&) when validating BareMetalHost ConsumerRef Kind and Group, meaning it only rejected a ConsumerRef when both Kind and Group were wrong. If only one was incorrect (e.g., wrong Kind but correct Group), the validation passed, potentially allowing unauthorized resources to associate with a BareMetalHost.

### 4. Cross-namespace Metal3DataTemplate references

Metal3DataClaim resources could reference Metal3DataTemplate resources in other namespaces. The controller would reconcile using the referenced template regardless of namespace, allowing data leakage across namespace boundaries.

## Impact

These vulnerabilities allow cross-namespace resource access within the CAPM3 management cluster. A user with permissions to create or modify Metal3Machine or Metal3DataClaim resources in one namespace could reference secrets, BareMetalHosts, or data templates in other namespaces.

Practical impact is limited because:

- CAPM3 management clusters are typically single-tenant, operated by a single infrastructure/platform team. Namespace boundaries serve as organizational separation (e.g., per workload cluster), not as security isolation between mutually untrusted parties.
- Exploiting these issues requires RBAC permissions to create or modify CAPM3 infrastructure resources (Metal3Machine, Metal3DataClaim), which are infrastructure-admin privileges not granted to application developers or end users.
- The accessible resources are limited to Metal3 operational artifacts (bootstrap secrets, network metadata, BareMetalHost associations), not arbitrary cluster secrets.

Environments with elevated risk:

- Management clusters where namespace-scoped RBAC is used to delegate infrastructure provisioning to separate teams with different trust levels.
- Managed service providers using a shared management cluster across multiple customer namespaces.

In the common single-team deployment model, these issues represent a defense-in-depth gap rather than a directly exploitable privilege escalation.

### Prerequisites for exploitation

- Attacker must have RBAC permissions to create or modify Metal3Machine or Metal3DataClaim resources in at least one namespace.
- Target resources (secrets, BareMetalHosts, templates) must exist in other namespaces on the same management cluster.

## Workarounds

If upgrading is not immediately possible:

1. Restrict RBAC: Limit who can create/modify Metal3Machine and Metal3DataClaim resources to trusted operators only.
2. Admission policies: Deploy OPA/Gatekeeper or Kyverno policies that reject CAPM3 resources with cross-namespace references.
3. Network policies: While not a direct mitigation, network policies can limit the blast radius of compromised credentials.

## Resources

- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3288, https://github.com/metal3-io/cluster-api-provider-metal3/pull/3294
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3317, https://github.com/metal3-io/cluster-api-provider-metal3/pull/3319, https://github.com/metal3-io/cluster-api-provider-metal3/pull/3323
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3322, https://github.com/metal3-io/cluster-api-provider-metal3/pull/3325
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3327, https://github.com/metal3-io/cluster-api-provider-metal3/pull/3343, https://github.com/metal3-io/cluster-api-provider-metal3/pull/3344

## References
- https://github.com/metal3-io/cluster-api-provider-metal3/security/advisories/GHSA-rf84-wr5g-m3rp
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3288
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3294
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3317
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3319
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3322
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3323
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3325
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3327
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3343
- https://github.com/metal3-io/cluster-api-provider-metal3/pull/3344
- https://github.com/metal3-io/cluster-api-provider-metal3
