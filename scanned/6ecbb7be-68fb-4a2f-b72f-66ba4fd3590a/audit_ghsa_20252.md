# [M] Calico vulnerable to pod route hijacking

## Summary
Severity: Medium
Advisory: GHSA-9394-xfq9-6qrp
CVE: CVE-2022-28224
CWE: CWE-20, CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2022-06-07
Source: https://github.com/advisories/GHSA-9394-xfq9-6qrp
Type: github-advisory

## Affected
- Go: `github.com/projectcalico/calico` — affected >=3.22.0 <3.22.2
- Go: `github.com/projectcalico/calico` — affected >=3.21.0 <3.21.5
- Go: `github.com/projectcalico/calico` — affected >=0 <3.20.5

## Details
Clusters using Calico (version 3.22.1 and below), Calico Enterprise (version 3.12.0 and below), may be vulnerable to route hijacking with the floating IP feature. Due to insufficient validation, a privileged attacker may be able to set a floating IP annotation to a pod even if the feature is not enabled. This may allow the attacker to intercept and reroute traffic to their compromised pod.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28224
- https://github.com/projectcalico/calico
- https://www.tigera.io/security-bulletins-tta-2022-001
