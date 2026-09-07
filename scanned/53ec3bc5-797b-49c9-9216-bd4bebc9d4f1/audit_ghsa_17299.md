# [M] Cilium with misconfigured toGroups in policies can lead to unrestricted egress traffic

## Summary
Severity: Medium
Advisory: GHSA-38pp-6gcp-rqvm
CVE: CVE-2025-64715
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-01
Source: https://github.com/advisories/GHSA-38pp-6gcp-rqvm
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.18.0 <1.18.4
- Go: `github.com/cilium/cilium` — affected >=1.17.0 <1.17.10
- Go: `github.com/cilium/cilium` — affected >=0 <1.16.17

## Details
### Impact

`CiliumNetworkPolicy`s which use `egress.toGroups.aws.securityGroupsIds` to reference AWS security group IDs that do not exist or are not attached to any network interface may unintentionally allow broader outbound access than intended by the policy authors. In such cases, the toCIDRset section of the derived policy is not generated, which means outbound traffic may be permitted to more destinations than originally intended.

### Patches

This issue has been patched in:

* Cilium v1.18.4
* Cilium v1.17.10
* Cilium v1.16.17

### This issue affects:

- Cilium v1.18 between v1.18.0 and v1.18.3 inclusive
- Cilium v1.17 between v1.17.0 and v1.17.9 inclusive
- Cilium v1.16.16 and below

### Workarounds

There is no workaround to this issue.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @SeanEmac   for reporting this issue and to @fristonio for the patch.

### For more information

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-38pp-6gcp-rqvm
- https://nvd.nist.gov/vuln/detail/CVE-2025-64715
- https://github.com/cilium/cilium/commit/a385856b59c8289cc7273fa3a3062bbf0ef96c97
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.16.17
- https://github.com/cilium/cilium/releases/tag/v1.17.10
- https://github.com/cilium/cilium/releases/tag/v1.18.4
