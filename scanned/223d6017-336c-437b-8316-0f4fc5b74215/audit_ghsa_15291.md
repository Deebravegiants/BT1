# [M] Cilium leaks information via incorrect ReferenceGrant update logic in Gateway API

## Summary
Severity: Medium
Advisory: GHSA-vwf8-q6fw-4wcm
CVE: CVE-2024-42486
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-16
Source: https://github.com/advisories/GHSA-vwf8-q6fw-4wcm
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.16.0 <1.16.1
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.8

## Details
### Impact

Due to ReferenceGrant changes not being immediately propagated in Cilium's GatewayAPI controller, Gateway resources are able to access secrets in other namespaces after the associated ReferenceGrant has been revoked. This can lead to Gateways continuing to establish sessions using secrets that they should no longer have access to.

### Patches

This issue was resolved in https://github.com/cilium/cilium/pull/34032.

This issue affects:

- Cilium v1.15 between v1.15.0 and v1.15.7 inclusive
- Cilium v1.16.0

This issue has been patched in:

- Cilium v1.15.8
- Cilium v1.16.1

### Workarounds

Any modification of a related Gateway/HTTPRoute/GRPCRoute/TCPRoute CRD (for example, adding any label to any of these resources) will trigger a reconciliation of ReferenceGrants on an affected cluster.

### Acknowledgements

The Cilium community has worked together with members of Cure53 and Isovalent to prepare these mitigations. Special thanks to @sayboras for resolving this issue.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-vwf8-q6fw-4wcm
- https://nvd.nist.gov/vuln/detail/CVE-2024-42486
- https://github.com/cilium/cilium/pull/34032
- https://github.com/cilium/cilium/commit/414a96b53d51ef6e6645c44426e26bc8e7c7c059
- https://github.com/cilium/cilium/commit/92c110e58a7be6586819dd51fb0f6ee1ec4be8f8
- https://github.com/cilium/cilium/commit/ed3dfa0aab8b80f7e841a6d49d2a990ac2dca053
- https://github.com/cilium/cilium
