# [M] Cilium vulnerable to information leakage via incorrect ReferenceGrant handling

## Summary
Severity: Medium
Advisory: BIT-cilium-2023-34242
Aliases: BIT-cilium-operator-2023-34242, BIT-cilium-proxy-2023-34242, BIT-hubble-2023-34242, BIT-hubble-relay-2023-34242, BIT-hubble-ui-2023-34242, BIT-hubble-ui-backend-2023-34242, CVE-2023-34242, GHSA-r7wr-4w5q-55m6
Ecosystem: Bitnami
Published: 2024-05-15
Source: https://osv.dev/vulnerability/BIT-cilium-2023-34242
Type: osv

## Affected
- Bitnami: `cilium` — affected >=0 <1.13.4

## Details
Cilium is a networking, observability, and security solution with an eBPF-based dataplane. Prior to version 1.13.4, when Gateway API is enabled in Cilium, the absence of a check on the namespace in which a ReferenceGrant is created could result in Cilium unintentionally gaining visibility of secrets (including certificates) and services across namespaces. An attacker on an affected cluster can leverage this issue to use cluster secrets that should not be visible to them, or communicate with services that they should not have access to. Gateway API functionality is disabled by default. This vulnerability is fixed in Cilium release 1.13.4. As a workaround, restrict the creation of `ReferenceGrant` resources to admin users by using Kubernetes RBAC.

## References
- https://github.com/cilium/cilium/releases/tag/v1.13.4
- https://github.com/cilium/cilium/security/advisories/GHSA-r7wr-4w5q-55m6
- https://nvd.nist.gov/vuln/detail/CVE-2023-34242
