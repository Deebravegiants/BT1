# [M] DoS in Cilium agent DNS proxy from crafted DNS responses

## Summary
Severity: Medium
Advisory: GHSA-9m5p-c77c-f9j7
CVE: CVE-2025-23028
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-9m5p-c77c-f9j7
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.14.0 <1.14.18
- Go: `github.com/cilium/cilium` — affected >=1.15.0 <1.15.12
- Go: `github.com/cilium/cilium` — affected >=1.16.0 <1.16.5

## Details
### Impact

In a Kubernetes cluster where Cilium is configured to proxy DNS traffic, an attacker can crash Cilium agents by sending a crafted DNS response to workloads from outside the cluster.

For traffic that is allowed but without using DNS-based policy, the dataplane will continue to pass traffic as configured at the time of the DoS. For workloads that have DNS-based policy configured, existing connections may continue to operate, and new connections made without relying on DNS resolution may continue to be established, but new connections which rely on DNS resolution may be disrupted. Any configuration changes that affect the impacted agent may not be applied until the agent is able to  restart.

### Patches

This issue affects:

- Cilium v1.14 between v1.14.0 and v1.14.17 inclusive
- Cilium v1.15 between v1.15.0 and v1.15.11 inclusive
- Cilium v1.16 between v1.16.0 and v1.16.4 inclusive

This issue is fixed in:

- Cilium v1.14.18
- Cilium v1.15.12
- Cilium v1.16.5

### Workarounds

There are no known workarounds to this issue.

### Acknowledgements

The Cilium community has worked together with members of Isovalent and the Cisco Advanced Security Initiatives Group (ASIG) to prepare these mitigations. Special thanks to @kokelley-cisco for reporting this issue and @bimmlerd for the fix.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

If you think you have found a vulnerability affecting Cilium, we strongly encourage you to report it to our security mailing list at [security@cilium.io](mailto:security@cilium.io). This is a private mailing list for the Cilium security team, and your report will be treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-9m5p-c77c-f9j7
- https://nvd.nist.gov/vuln/detail/CVE-2025-23028
- https://github.com/cilium/cilium/pull/36252
- https://github.com/cilium/cilium/commit/1971bc684b6b36703ebae0dd7539c623f988a257
- https://github.com/cilium/cilium/commit/b1948e217a4212b81175d8bf763d0ef350fcc96c
- https://github.com/cilium/cilium
