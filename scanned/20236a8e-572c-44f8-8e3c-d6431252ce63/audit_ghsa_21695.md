# [M] Exposure of Sensitive Information to an Unauthorized Actor and Insertion of Sensitive Information Into Sent Data in Calico

## Summary
Severity: Medium
Advisory: GHSA-pf59-j7c2-rh6x
CVE: CVE-2020-13597
CWE: CWE-200, CWE-201
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-pf59-j7c2-rh6x
Type: github-advisory

## Affected
- Go: `github.com/projectcalico/calico` — affected >=3.14.0 <3.14.1
- Go: `github.com/projectcalico/calico` — affected >=3.13.0 <3.13.4
- Go: `github.com/projectcalico/calico` — affected >=3.12.0 <3.12.2
- Go: `github.com/projectcalico/calico` — affected >=3.11.0 <3.11.3
- Go: `github.com/projectcalico/calico` — affected >=3.10.0 <3.10.4
- Go: `github.com/projectcalico/calico` — affected >=3.9.0 <3.9.6
- Go: `github.com/projectcalico/calico` — affected >=0 <3.8.9

## Details
Clusters using Calico (version 3.14.0 and below), Calico Enterprise (version 2.8.2 and below), may be vulnerable to information disclosure if IPv6 is enabled but unused. A compromised pod with sufficient privilege is able to reconfigure the node’s IPv6 interface due to the node accepting route advertisement by default, allowing the attacker to redirect full or partial network traffic from the node to the compromised pod.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13597
- https://github.com/kubernetes/kubernetes/issues/91507
- https://github.com/containernetworking/plugins/pull/484
- https://github.com/containernetworking/plugins/commit/ad10b6fa91aacd720f1f9ab94341a97a82a24965
- https://github.com/projectcalico/calico
- https://groups.google.com/forum/#!topic/kubernetes-security-announce/BMb_6ICCfp8
- https://www.projectcalico.org/security-bulletins
