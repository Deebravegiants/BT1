# [M] Unencrypted traffic between pods when using Wireguard and an external kvstore

## Summary
Severity: Medium
Advisory: GHSA-x989-52fc-4vr4
CVE: CVE-2024-25631
CWE: CWE-311, CWE-319
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-x989-52fc-4vr4
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.7

## Details
### Impact

For Cilium users who have enabled [an external kvstore](https://docs.cilium.io/en/stable/installation/k8s-install-external-etcd/#when-do-i-need-to-use-a-kvstore) and [Wireguard transparent encryption](https://docs.cilium.io/en/stable/security/network/encryption-wireguard/#encryption-wg), traffic between pods in the affected cluster is not encrypted.

### Patches

This issue affects Cilium v1.14 before v1.14.7.

This issue has been patched in Cilium v1.14.7.

### Workarounds

There is no workaround to this issue - affected users are encouraged to upgrade.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @giorio94 and @gandro for their work on triaging and remediating this issue.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list where only members of the Cilium internal security team are subscribed to, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-x989-52fc-4vr4
- https://nvd.nist.gov/vuln/detail/CVE-2024-25631
- https://docs.cilium.io/en/stable/installation/k8s-install-external-etcd/#when-do-i-need-to-use-a-kvstore
- https://docs.cilium.io/en/stable/security/network/encryption-wireguard/#encryption-wg
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.14.7
