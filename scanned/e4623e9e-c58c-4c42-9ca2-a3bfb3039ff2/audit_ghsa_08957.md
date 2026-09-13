# [M] Kong Ingress Controller for Kubernetes (KIC): Cross-namespace TLS Secret Exfiltration in Gateways with GatewayClass missing `konghq.com/gatewayclass-unmanaged: 'true'` annotation

## Summary
Severity: Medium
Advisory: GHSA-m23h-6mwm-39m8
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-m23h-6mwm-39m8
Type: github-advisory

## Affected
- Go: `github.com/kong/kubernetes-ingress-controller/v3` — affected >=3.5.0 <3.5.7
- Go: `github.com/kong/kubernetes-ingress-controller/v3` — affected >=0 <3.4.14
- Go: `github.com/kong/kubernetes-ingress-controller/v2` — affected >=0
- Go: `github.com/kong/kubernetes-ingress-controller` — affected >=0

## Details
## Summary

A vulnerability in the Kong Ingress Controller (KIC) allows for the unauthorized exfiltration of TLS certificates and private keys across Kubernetes namespace boundaries. In "managed" mode (where the `GatewayClass` lacks an unmanaged annotation), the Gateway TLS translator skips critical status checks. This bypass allows the translator to fetch Secrets from any namespace KIC watches, even when a `ReferenceGrant` explicitly denies access or is missing.

An actor with RBAC permissions to create or modify Gateways in a low-privileged namespace can reference a Secret in a high-privileged namespace, causing KIC to "leak" that Secret's sensitive private key material into the Kong dataplane configuration.

## Am I affected?

You are affected if all of these hold:
1. You are using Kong Ingress Controller with the **Gateway API**.
2. Your `GatewayClass` is operating in **managed mode** (default behavior, no unmanaged annotation).
3. KIC is configured to **watch multiple namespaces** (multi-tenant environment).
4. Users have RBAC permissions to `create` or `update` `gateways.gateway.networking.k8s.io` in their own namespaces.

You are not affected if any of this:
- You only use KIC for `Ingress` resources (not Gateway API).
- Your `GatewayClass` uses the `konghq.com/gateway-unmanaged` annotation.
- KIC is restricted via RBAC or configuration to only watch a single namespace.
- You have strictly limited Gateway creation/modification permissions to trusted cluster administrators only.

## Mitigation

1. **Add unmanaged gateway annotation**: add the `konghq.com/gateway-unmanaged` annotation to your `GatewayClass`

### Additional best practicies

1. **Restrict Gateway RBAC**: Limit the ability to create or modify Gateway resources to high-trust administrative users until a patch is applied.
2. **Namespace Isolation**: If possible, limit the namespaces KIC is permitted to watch using the `WATCH_NAMESPACE` environment variable or specific RBAC RoleBindings.

## Fix

The fix mandates `ReferenceGrant` validation for all cross-namespace certificate references. By requiring a `Programmed: True` listener status, the translator now strictly authorizes external Secret access while maintaining default access for same-namespace certificates, effectively closing the exfiltration vector.

Fixed in [#7920](https://github.com/Kong/kubernetes-ingress-controller/pull/7920), with backports to supported release branches in [#7921](https://github.com/Kong/kubernetes-ingress-controller/pull/7921) and [#7922](https://github.com/Kong/kubernetes-ingress-controller/pull/7922).

Upgrade to one of the following patched versions (or later):
- **3.4.14**
- **3.5.7**

## CVSS

`CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:P` = **5.6 Medium**

## References
- https://github.com/Kong/kubernetes-ingress-controller/security/advisories/GHSA-m23h-6mwm-39m8
- https://github.com/Kong/kubernetes-ingress-controller/pull/7920
- https://github.com/Kong/kubernetes-ingress-controller/pull/7921
- https://github.com/Kong/kubernetes-ingress-controller/pull/7922
- https://github.com/Kong/kubernetes-ingress-controller
