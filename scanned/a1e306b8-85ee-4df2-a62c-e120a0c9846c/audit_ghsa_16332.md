# [M] Unencrypted ingress/health traffic when using Wireguard transparent encryption

## Summary
Severity: Medium
Advisory: GHSA-7496-fgv9-xw82
CVE: CVE-2024-25630
CWE: CWE-311, CWE-319
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-7496-fgv9-xw82
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.7

## Details
### Impact

For Cilium users who are using CRDs to store Cilium state (the default configuration) and [Wireguard transparent encryption](https://docs.cilium.io/en/stable/security/network/encryption-wireguard/#encryption-wg), responses from pods to the Ingress and health endpoints are not encrypted. Traffic from the Ingress and health endpoints to pods is not affected by this issue. The health endpoint is only used for Cilium's internal health checks.

### Patches

This issue affects Cilium v1.14 before v1.14.7.

This issue has been patched in Cilium v1.14.7.

### Workarounds

There is no workaround to this issue - affected users are encouraged to upgrade.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @gandro for their work on triaging and remediating this issue.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list where only members of the Cilium internal security team are subscribed to, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-7496-fgv9-xw82
- https://nvd.nist.gov/vuln/detail/CVE-2024-25630
- https://docs.cilium.io/en/stable/security/network/encryption-wireguard/#encryption-wg
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.14.7
