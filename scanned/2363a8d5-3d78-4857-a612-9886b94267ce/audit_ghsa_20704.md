# [M] Network Policies & (Clusterwide) Cilium Network Policies with namespace label selectors may unexpectedly select pods with maliciously crafted labels

## Summary
Severity: Medium
Advisory: GHSA-pfhr-pccp-hwmh
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-pfhr-pccp-hwmh
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=0 <1.10.14
- Go: `github.com/cilium/cilium` — affected >=1.11.0 <1.11.8
- Go: `github.com/cilium/cilium` — affected >=1.12.0 <1.12.1

## Details
### Impact

If a user has Network Policies with namespace selectors selecting labels of namespaces, or (clusterwide) Cilium Network Policies matching on namespace labels, then it is possible for an attacker with Kubernetes pod deploy rights (either directly or indirectly via higher-level APIs such as Deployment, Daemonset etc) to craft additional pod labels such that the pod is selected by another policy that exists rather than the expected policy. 

### Patches

The problem has been fixed and is available on versions >=1.10.14, >=1.11.8, >=1.12.1

### Workarounds

There are no workarounds available.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to Sander Mathijssen for not only highlighting the issue but also proposing a resolution. 

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

As usual, if you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list: [security@cilium.io](mailto:security@cilium.io) - first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-pfhr-pccp-hwmh
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.10.14
- https://github.com/cilium/cilium/releases/tag/v1.11.8
- https://github.com/cilium/cilium/releases/tag/v1.12.1
