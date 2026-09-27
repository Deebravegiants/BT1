# [H] Constallation has pods exposed to peers in VPC

## Summary
Severity: High
Advisory: GHSA-g8fc-vrcg-8vjg
CWE: CWE-940
Ecosystem: Go
Published: 2024-04-15
Source: https://github.com/advisories/GHSA-g8fc-vrcg-8vjg
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/constellation/v2` — affected >=0 <2.16.3

## Details
### Impact

Cilium allows outside actors (`world` entity) to directly access pods with their internal pod IP, even if they are not exposed explicitly (e.g. via `LoadBalancer`). A pod that does not authenticate clients and that does not exclude `world` traffic via network policy may leak sensitive data to an attacker _inside the cloud VPC_.

### Patches

The issue has been patched in [v2.16.3](https://github.com/edgelesssys/constellation/releases/tag/v2.16.3).

### Workarounds

This network policy excludes all `world` traffic. It mitigates the problem, but will also block all desired external traffic. If vulnerable pods are known, a policy can be crafted to only firewall those instead (see also https://docs.cilium.io/en/stable/security/policy/language/#access-to-from-outside-cluster).

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: "from-world-to-role-public"
spec:
  endpointSelector:
    matchLabels: {}
    #  role: public
  ingressDeny:
    - fromEntities:
      - world
```

### References

The tracking bug for a Cilium-side fix is https://github.com/cilium/cilium/issues/25626.

## References
- https://github.com/edgelesssys/constellation/security/advisories/GHSA-g8fc-vrcg-8vjg
- https://github.com/cilium/cilium/issues/25626
- https://github.com/edgelesssys/constellation
- https://pkg.go.dev/vuln/GO-2024-2727
