# [M] cilium-agent container can access the host via `hostPath` mount

## Summary
Severity: Medium
Advisory: GHSA-4hc4-pgfx-3mrx
CVE: CVE-2023-27593
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-4hc4-pgfx-3mrx
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=0 <1.11.15
- Go: `github.com/cilium/cilium` — affected >=1.12.0 <1.12.8
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.13.1

## Details
### Impact

An attacker with access to a Cilium agent pod can write to `/opt/cni/bin` due to a `hostPath` mount of that directory in the agent pod. By replacing the CNI binary with their own malicious binary and waiting for the creation of a new pod on the node, the attacker can gain access to the underlying node. 

### Patches

The issue has been fixed and is available on versions >=1.11.15, >=1.12.8, >=1.13.1.

### Workarounds

[Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) should be used to deny users and service accounts `exec` access to Cilium agent pods.

In cases where a user requires `exec` access to Cilium agent pods, but should not have access to the underlying node, no workaround is possible.

### References

* [PR containing resolution](https://github.com/cilium/cilium/pull/24075)

### Acknowledgements

The Cilium community has worked together with members of Isovalent and Form3 to prepare these mitigations. Special thanks to Anastasios Koutlis, Daniel Teixeira, and Magdalena Oczadly for their cooperation. 

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

As usual, if you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list: security@cilium.io - first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-4hc4-pgfx-3mrx
- https://nvd.nist.gov/vuln/detail/CVE-2023-27593
- https://github.com/cilium/cilium/pull/24075
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.11.15
- https://github.com/cilium/cilium/releases/tag/v1.12.8
- https://github.com/cilium/cilium/releases/tag/v1.13.1
- https://kubernetes.io/docs/reference/access-authn-authz/rbac
