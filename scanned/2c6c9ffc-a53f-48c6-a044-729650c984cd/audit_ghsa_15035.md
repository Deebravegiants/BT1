# [H] Cilium leaks sensitive information in cilium-bugtool

## Summary
Severity: High
Advisory: GHSA-wh78-7948-358j
CVE: CVE-2024-37307
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-13
Source: https://github.com/advisories/GHSA-wh78-7948-358j
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.13.17
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.12
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.6

## Details
### Impact

The output of `cilium-bugtool` can contain sensitive data when the tool is run (with the `--envoy-dump` flag set) against Cilium deployments with the Envoy proxy enabled.

Users of the following features are affected:

- [TLS inspection](https://docs.cilium.io/en/stable/security/tls-visibility/#gs-tls-inspection)
- [Ingress with TLS termination](https://docs.cilium.io/en/stable/network/servicemesh/tls-termination/#gs-ingress-tls)
- [Gateway API with TLS termination](https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/https/)
- [Kafka network policies with API key filtering](https://docs.cilium.io/en/stable/security/policy/language/#kafka-beta)

The sensitive data includes:

- The CA certificate, certificate chain, and private key used by Cilium HTTP Network Policies, and when using Ingress/Gateway API
- The API keys used in Kafka-related network policy

`cilium-bugtool` is a debugging tool that is typically invoked manually and does not run during the normal operation of a Cilium cluster.

### Patches

This issue affects:

- Cilium v1.13 between v1.13.0 and v1.13.16 inclusive
- Cilium v1.14 between v1.14.0 and v1.14.11 inclusive
- Cilium v1.15 between v1.15.0 and v1.15.5 inclusive

This issue has been patched in:

- Cilium v1.15.6
- Cilium v1.14.12
- Cilium v1.13.17

### Workarounds

There is no workaround to this issue.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @sayboras for their work on triaging and remediating this issue.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-wh78-7948-358j
- https://nvd.nist.gov/vuln/detail/CVE-2024-37307
- https://github.com/cilium/cilium/commit/0191b1ebcfdd61cefd06da0315a0e7d504167407
- https://github.com/cilium/cilium/commit/224e288a5bf40d0bb0f16c9413693b319633431a
- https://github.com/cilium/cilium/commit/9299c0fd0024e33397cffc666ff851e82af28741
- https://github.com/cilium/cilium/commit/958d7b77274bf2c272d8cdfd812631d644250653
- https://github.com/cilium/cilium/commit/9eb25ba40391a9b035d7e66401b862818f4aac4b
- https://github.com/cilium/cilium/commit/bf9a1ae1b2d2b2c9cca329d7aa96aa4858032a61
- https://github.com/cilium/cilium
- https://pkg.go.dev/vuln/GO-2024-2922
