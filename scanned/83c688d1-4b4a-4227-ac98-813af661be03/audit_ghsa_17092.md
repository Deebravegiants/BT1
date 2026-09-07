# [M] Unencrypted traffic between nodes when using WireGuard and L7 policies

## Summary
Severity: Medium
Advisory: GHSA-v6q2-4qr3-5cw6
CVE: CVE-2024-28250
CWE: CWE-311, CWE-319
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-v6q2-4qr3-5cw6
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.8
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.2

## Details
### Impact

In Cilium clusters with WireGuard enabled and traffic matching Layer 7 policies:

- Traffic that should be WireGuard-encrypted is sent unencrypted between a node's Envoy proxy and pods on other nodes.
- Traffic that should be WireGuard-encrypted is sent unencrypted between a node's DNS proxy and pods on other nodes.

### Patches

This issue affects:

* In native routing mode (`routingMode=native`):
  * Cilium v1.14 versions before v1.14.8
  * Cilium v1.15 versions before v1.15.2
* In tunneling mode (`routingMode=tunnel`):
  * Cilium v1.14 versions before v1.14.4
  * Cilium v1.14.4 if `encryption.wireguard.encapsulate` is set to `false` (default).

This issue has been resolved in:

* In native routing mode (`routingMode=native`):
  * Cilium v1.14.8
  * Cilium v1.15.2
* In tunneling mode (`routingMode=tunnel`):
  * Cilium v1.14.4. **NOTE** `encryption.wireguard.encapsulate` must be set to `true`.
   
### Workarounds

There is no workaround to this issue.

### Acknowledgements
The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @brb, @giorio94, @gandro and @jschwinger233 for their work on triaging and remediating this issue.

### For more information
If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list where only members of the Cilium internal security team are subscribed to, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-v6q2-4qr3-5cw6
- https://nvd.nist.gov/vuln/detail/CVE-2024-28250
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.13.13
- https://github.com/cilium/cilium/releases/tag/v1.14.8
- https://github.com/cilium/cilium/releases/tag/v1.15.2
