# [M] Policy bypass for Host Firewall policy due to race condition in Cilium agent

## Summary
Severity: Medium
Advisory: GHSA-q7w8-72mr-vpgw
CVE: CVE-2024-42488
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-15
Source: https://github.com/advisories/GHSA-q7w8-72mr-vpgw
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=0 <1.14.14
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.8

## Details
### Impact

A race condition in the Cilium agent can cause the agent to ignore labels that should be applied to a node. This could in turn cause CiliumClusterwideNetworkPolicies intended for nodes with the ignored label to not apply, leading to policy bypass.

### Patches

This issue was fixed in https://github.com/cilium/cilium/pull/33511.

This issue affects:

- All versions of Cilium before v1.14.14
- Cilium v1.15 between v1.15.0 and v1.15.7 inclusive

This issue has been patched in:

- Cilium v1.14.14
- Cilium v1.15.8

### Workarounds

As the underlying issue depends on a race condition, users unable to upgrade can restart the Cilium agent on affected nodes until the affected policies are confirmed to be working as expected.

### Acknowledgements

The Cilium community has worked together with members of Google and Isovalent to prepare these mitigations. Special thanks to @skmatti for raising and resolving this issue.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-q7w8-72mr-vpgw
- https://nvd.nist.gov/vuln/detail/CVE-2024-42488
- https://github.com/cilium/cilium/pull/33511
- https://github.com/cilium/cilium/commit/7877db09b3f34d3081a1d66459b8fa6603dc3d30
- https://github.com/cilium/cilium/commit/aa44dd148a9be95e07782e4f990e61678ef0abf8
- https://github.com/cilium/cilium/commit/f81a1ee0cfdec928980db8640def984b2eeaa134
- https://github.com/cilium/cilium
