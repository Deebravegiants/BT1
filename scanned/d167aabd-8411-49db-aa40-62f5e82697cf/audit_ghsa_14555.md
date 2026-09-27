# [M] `cilium-cli` disables etcd authorization for clustermesh clusters

## Summary
Severity: Medium
Advisory: GHSA-6f27-3p6c-p5jc
CVE: CVE-2023-28114
CWE: CWE-280
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-21
Source: https://github.com/advisories/GHSA-6f27-3p6c-p5jc
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium-cli` — affected >=0 <0.13.2

## Details
### Impact

`cilium-cli`, when used to configure cluster mesh functionality, can remove the enforcement of user permissions on the `etcd` store used to mirror local cluster information to remote clusters. 

Due to an incorrect mount point specification, the settings specified by the `initContainer` that configures `etcd` users and their permissions are overwritten when using `cilium-cli` to configure a cluster mesh. An attacker who has already gained access to a valid key and certificate for an `etcd` cluster compromised in this manner could then modify state in that `etcd` cluster.

### Patches

This issue is patched in `cilium-cli` 0.13.2

All previous versions of `cilium-cli` are affected. Users who have set up cluster meshes using the Cilium Helm chart are not affected.

### Workarounds

Use Cilium's [Helm charts](https://artifacthub.io/packages/helm/cilium/cilium) to create your cluster instead.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to Marco Iorio for investigating and fixing the issue.

### For more information
If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

As usual, if you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list: [security@cilium.io](mailto:security@cilium.io) - first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium-cli/security/advisories/GHSA-6f27-3p6c-p5jc
- https://nvd.nist.gov/vuln/detail/CVE-2023-28114
- https://github.com/cilium/cilium-cli/commit/fb1427025764e1eebc4a7710d902c4f22cae2610
- https://artifacthub.io/packages/helm/cilium/cilium
- https://github.com/cilium/cilium-cli
- https://github.com/cilium/cilium-cli/releases/tag/v0.13.2
