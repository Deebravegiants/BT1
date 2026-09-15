# [M] Cilium eBPF filters may be temporarily removed during agent restart

## Summary
Severity: Medium
Advisory: GHSA-r5x6-w42p-jhpp
CVE: CVE-2023-27595
CWE: CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-r5x6-w42p-jhpp
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.13.1

## Details
### Impact

When Cilium is started, there is a short period when Cilium eBPF programs are not attached to the host. During this period, the host does not implement any of Cilium's featureset. This can cause disruption to newly established connections during this period due to the lack of Load Balancing, or can cause Network Policy bypass due to the lack of Network Policy enforcement during the window. This vulnerability impacts any Cilium-managed endpoints on the node (such as Kubernetes Pods), as well as the host network namespace (including Host Firewall).

### Patches

This vulnerability is fixed by https://github.com/cilium/cilium/pull/24336, included in Cilium 1.13.1 or later. Cilium releases 1.12.x, 1.11.x and earlier are not affected.

### Workarounds

There are no known workarounds.

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to Louis DeLosSantos and Timo Beckers for investigating and fixing the issue.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

As usual, if you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list: security@cilium.io - first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-r5x6-w42p-jhpp
- https://nvd.nist.gov/vuln/detail/CVE-2023-27595
- https://github.com/cilium/cilium/pull/24336
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.13.1
