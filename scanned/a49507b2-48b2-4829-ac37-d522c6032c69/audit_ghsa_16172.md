# [M] Cilium's Layer 7 policy enforcement may not occur in policies with wildcarded port ranges

## Summary
Severity: Medium
Advisory: GHSA-xg58-75qf-9r67
CVE: CVE-2024-52529
CWE: CWE-755, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-xg58-75qf-9r67
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.16.0 <1.16.4

## Details
### Impact

For users with the following configuration:

* An allow policy that selects a [Layer 3 identity](https://docs.cilium.io/en/v1.14/security/policy/language/#layer-3-examples) and a [port range](https://docs.cilium.io/en/stable/security/policy/language/#example-port-ranges) **AND**
* A [Layer 7 allow policy](https://docs.cilium.io/en/latest/security/policy/language/#layer-7-examples) that selects a specific port within the first policy's range 

then Layer 7 enforcement would not occur for the traffic selected by the Layer 7 policy.

This issue only affects users who use Cilium's port range functionality, which was introduced in Cilium v1.16.

For reference, an example of a pair of policies that would trigger this issue is:

```
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "layer-3-and-4"
spec:
  endpointSelector:
    matchLabels:
      app: service
  ingress:
    - fromCIDR:
      - 192.168.60.0/24
      toPorts:
      - ports:
        - port: "80"
          endPort: 444
          protocol: TCP
```
and
```
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "layer-4-and-7"
spec:
  endpointSelector:
    matchLabels:
      app: service
  ingress:
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/public"
```

In the above example, requests would be permitted to all HTTP paths on matching endpoints, rather than just `GET` requests to the `/public` path as intended by the `layer-4-and-7` policy. In patched versions of Cilium, the `layer-4-and-7` rule would take precedence over the `layer-3-and-4` rule.

### Patches

This issue is patched in https://github.com/cilium/cilium/pull/35150.

This issue affects Cilium v1.16 between v1.16.0 and v1.16.3 inclusive.

This issue is patched in Cilium v1.16.4.

### Workarounds

Users with network policies that match the pattern described above can work around the issue by rewriting any policies that use port ranges to individually specify the ports permitted for traffic.

### Acknowledgements
The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @jrajahalme for resolving this issue.

### For more information
If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-xg58-75qf-9r67
- https://nvd.nist.gov/vuln/detail/CVE-2024-52529
- https://github.com/cilium/cilium/pull/35150
- https://github.com/cilium/cilium
