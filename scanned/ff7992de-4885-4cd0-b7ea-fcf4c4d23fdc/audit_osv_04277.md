# [M] BIT-cilium-2024-28249

## Summary
Severity: Medium
Advisory: BIT-cilium-2024-28249
Aliases: BIT-cilium-operator-2024-28249, BIT-cilium-proxy-2024-28249, BIT-hubble-2024-28249, BIT-hubble-relay-2024-28249, BIT-hubble-ui-2024-28249, BIT-hubble-ui-backend-2024-28249, CVE-2024-28249, GHSA-j89h-qrvr-xc36
Ecosystem: Bitnami
Published: 2024-05-15
Source: https://osv.dev/vulnerability/BIT-cilium-2024-28249
Type: osv

## Affected
- Bitnami: `cilium` — affected >=1.15.0 <1.15.2

## Details
Cilium is a networking, observability, and security solution with an eBPF-based dataplane. Prior to versions 1.13.13, 1.14.8, and 1.15.2, in Cilium clusters with IPsec enabled and traffic matching Layer 7 policies, IPsec-eligible traffic between a node's Envoy proxy and pods on other nodes is sent unencrypted and IPsec-eligible traffic between a node's DNS proxy and pods on other nodes is sent unencrypted. This issue has been resolved in Cilium 1.15.2, 1.14.8, and 1.13.13. There is no known workaround for this issue.

## References
- https://github.com/cilium/cilium/releases/tag/v1.13.13
- https://github.com/cilium/cilium/releases/tag/v1.14.8
- https://github.com/cilium/cilium/releases/tag/v1.15.2
- https://github.com/cilium/cilium/security/advisories/GHSA-j89h-qrvr-xc36
