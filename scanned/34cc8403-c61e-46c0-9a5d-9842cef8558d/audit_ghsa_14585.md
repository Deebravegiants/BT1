# [M] Potential network policy bypass when routing IPv6 traffic 

## Summary
Severity: Medium
Advisory: GHSA-8fg8-jh2h-f2hc
CVE: CVE-2023-27594
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-8fg8-jh2h-f2hc
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=0 <1.11.15
- Go: `github.com/cilium/cilium` — affected >=1.12.0 <1.12.8
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.13.1

## Details
## Impact

Under specific conditions, Cilium may misattribute the source IP address of traffic to a cluster, identifying external traffic as coming from the host on which Cilium is running. As a consequence, network policies for that cluster might be bypassed, depending on the specific network policies enabled. Only IPv6 traffic is impacted by this vulnerability.

This issue only manifests when:
* Cilium is routing IPv6 traffic, and
* Kube-proxy is used for service handling, and
* NodePorts are used to route traffic to pods.

IPv6 is disabled by default. Cilium's kube-proxy replacement feature is not affected by this vulnerability.

## Patches

The problem has been fixed and is available on versions >=1.11.15, >=1.12.8, >=1.13.1

## Workarounds

Disable IPv6 routing (IPv6 is disabled by default).

## Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to Yusuke Suzuki for both highlighting and fixing the issue.

## For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

As usual, if you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list: security@cilium.io - first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-8fg8-jh2h-f2hc
- https://nvd.nist.gov/vuln/detail/CVE-2023-27594
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.11.15
- https://github.com/cilium/cilium/releases/tag/v1.12.8
- https://github.com/cilium/cilium/releases/tag/v1.13.1
